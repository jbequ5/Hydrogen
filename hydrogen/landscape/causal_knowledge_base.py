"""Causal Knowledge Base with publishable (noisy) leading priors.

Designed so the full Landscape stays proprietary, while still allowing
miners to build off the current leader in a controlled way.

Publishing strategy: Daily per challenge + backbone with added noise.
"""

import json
import os
import time
import random
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

try:
    from econml.dml import LinearDML
    ECONML_AVAILABLE = True
except ImportError:
    ECONML_AVAILABLE = False

try:
    from pysr import PySRRegressor
    PYSR_AVAILABLE = True
except ImportError:
    PYSR_AVAILABLE = False


from .storage import save_symbolic_artifact, load_symbolic_artifacts


class CausalKnowledgeBase:
    """
    Challenge- and backbone-aware causal knowledge base.

    Supports publishing noisy versions of the current best priors daily.
    Full access remains proprietary. Miners only see the published version.
    """

    def __init__(self, storage_dir: str = "./data/landscape"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.causal_estimates: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def _make_key(self, challenge_id: str, backbone: str = "PINO") -> Tuple[str, str]:
        return (challenge_id, backbone)

    def add_observation(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        features: Dict[str, float] = None,
        treatment: Dict[str, float] = None,
        outcome: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        features = features or {}
        treatment = treatment or {}

        artifact = {
            "challenge_id": challenge_id,
            "backbone": backbone,
            "features": features,
            "treatment": treatment,
            "outcome": outcome,
            "metadata": metadata or {},
            "timestamp": int(time.time()),
        }

        save_symbolic_artifact(
            artifact_type="causal_observation",
            challenge_id=challenge_id,
            content=artifact,
            metadata={"source": "training_run", "backbone": backbone},
        )

    def estimate_causal_effects(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        treatment_key: str = "pde_residual_weight",
        min_samples: int = 30,
    ) -> Dict[str, Any]:
        key = self._make_key(challenge_id, backbone)
        artifacts = load_symbolic_artifacts(
            artifact_type="causal_observation",
            challenge_id=challenge_id,
            limit=1000,
        )

        filtered = [
            a for a in artifacts
            if a.get("content", {}).get("backbone", "default") == backbone
        ]
        if len(filtered) < min_samples:
            filtered = artifacts

        if len(filtered) < min_samples:
            return {
                "status": "insufficient_data",
                "n_observations": len(filtered),
                "challenge_id": challenge_id,
                "backbone": backbone,
            }

        X, T, Y = [], [], []
        for art in filtered:
            content = art.get("content", {})
            if treatment_key not in content.get("treatment", {}):
                continue

            feat_vec = list(content.get("features", {}).values())
            t_val = content["treatment"][treatment_key]
            y_val = content["outcome"]

            X.append(feat_vec)
            T.append(t_val)
            Y.append(y_val)

        if len(Y) < min_samples:
            return {"status": "insufficient_data_after_filtering", "n": len(Y)}

        X = np.array(X)
        T = np.array(T).ravel()
        Y = np.array(Y)

        method_used = "simple_residual_on_residual"
        ate = 0.0

        if ECONML_AVAILABLE:
            try:
                model = LinearDML(model_y="auto", model_t="auto", random_state=42)
                model.fit(Y, T, X=X)
                ate = float(model.ate(X))
                method_used = "LinearDML"
            except Exception:
                pass

        if method_used == "simple_residual_on_residual":
            from sklearn.linear_model import Ridge
            from sklearn.model_selection import cross_val_predict

            mu_y = cross_val_predict(Ridge(), X, Y, cv=5)
            mu_t = cross_val_predict(Ridge(), X, T, cv=5)
            residual_y = Y - mu_y
            residual_t = T - mu_t
            ate = np.mean(residual_y * residual_t) / (np.var(residual_t) + 1e-8)

        result = {
            "status": "success",
            "method": method_used,
            "ate": ate,
            "n_samples": len(Y),
            "challenge_id": challenge_id,
            "backbone": backbone,
            "treatment": treatment_key,
            "timestamp": int(time.time()),
        }

        self.causal_estimates[key] = result
        save_symbolic_artifact(
            artifact_type="causal_estimate",
            challenge_id=challenge_id,
            content=result,
            metadata={"backbone": backbone, "source": "CausalKnowledgeBase"},
        )
        return result

    def get_best_priors(
        self,
        challenge_id: str,
        backbone: str = "PINO",
    ) -> Dict[str, Any]:
        key = self._make_key(challenge_id, backbone)
        causal = self.causal_estimates.get(key, {})

        scoring = load_symbolic_artifacts(
            artifact_type="pysr_scoring",
            challenge_id=challenge_id,
            limit=5,
        )
        weights = load_symbolic_artifacts(
            artifact_type="evolved_loss_weights",
            challenge_id=challenge_id,
            limit=5,
        )

        best_loss_vector = {}
        if weights:
            best_loss_vector = weights[0].get("content", {}).get("loss_vector", {})

        best_scoring_expr = None
        if scoring:
            best_scoring_expr = scoring[0].get("content", {}).get("expression")

        return {
            "challenge_id": challenge_id,
            "backbone": backbone,
            "causal_estimate": causal,
            "recommended_loss_vector": best_loss_vector,
            "recommended_scoring_expression": best_scoring_expr,
            "last_updated": causal.get("timestamp") or int(time.time()),
        }

    def get_publishable_priors(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        noise_level: float = 0.03,
    ) -> Dict[str, Any]:
        """
        Return a noisy version of the current best priors.

        This is what should be published daily per challenge + backbone.
        The noise prevents exact copying while still giving miners a strong
        starting point (they are incentivized to improve upon it).
        """
        best = self.get_best_priors(challenge_id, backbone=backbone)

        # Add noise to loss vector
        noisy_loss = {}
        for k, v in best.get("recommended_loss_vector", {}).items():
            noise = random.gauss(0, noise_level)
            noisy_loss[k] = max(0.05, v * (1 + noise))

        return {
            "challenge_id": challenge_id,
            "backbone": backbone,
            "loss_vector": noisy_loss,
            "scoring_expression": best.get("recommended_scoring_expression"),
            "noise_level": noise_level,
            "published_at": int(time.time()),
            "based_on": best.get("last_updated"),
        }

    def update_from_observations(self, challenge_id: str, backbone: str = "PINO"):
        return self.estimate_causal_effects(challenge_id, backbone=backbone)
