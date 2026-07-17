"""Causal Knowledge Base for Hydrogen (SOTA Double ML + Symbolic).

Builds and maintains a causal understanding of what drives performance
across challenges using Double Machine Learning + PySR.

This is the core of the Landscape agent's reasoning capability.
"""

import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

try:
    from econml.dml import LinearDML
    from econml.cate import CATEEstimator
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
    Maintains a causal knowledge base using Double ML and symbolic methods.

    Capabilities:
    - Estimate causal effects of design choices (loss weights, etc.)
    - Discover heterogeneous treatment effects
    - Integrate PySR symbolic expressions
    - Provide best priors to miners and validators
    """

    def __init__(self, storage_dir: str = "./data/landscape"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.causal_estimates: Dict[str, Dict[str, Any]] = {}

    def add_observation(
        self,
        challenge_id: str,
        features: Dict[str, float],
        treatment: Dict[str, float],
        outcome: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a new observation (e.g. from a training run).

        features: context variables (e.g. Reynolds number, permeability contrast)
        treatment: variables whose causal effect we want to estimate (loss weights)
        outcome: performance metric (improvement or negative error)
        """
        artifact = {
            "challenge_id": challenge_id,
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
            metadata={"source": "training_run"},
        )

    def estimate_causal_effects(
        self,
        challenge_id: str,
        treatment_key: str = "pde_residual_weight",
        n_iterations: int = 50,
    ) -> Dict[str, Any]:
        """
        Estimate causal effect of a treatment variable using Double ML.

        Uses econml's LinearDML when available (SOTA), otherwise falls back
        to a simpler residual-on-residual approach.
        """
        artifacts = load_symbolic_artifacts(
            artifact_type="causal_observation",
            challenge_id=challenge_id,
            limit=500,
        )

        if len(artifacts) < 20:
            return {"status": "insufficient_data", "n_observations": len(artifacts)}

        # Build dataset
        X = []  # confounders / features
        T = []  # treatment
        Y = []  # outcome

        for art in artifacts:
            content = art.get("content", {})
            if treatment_key not in content.get("treatment", {}):
                continue

            features = list(content.get("features", {}).values())
            treatment_val = content["treatment"][treatment_key]
            outcome_val = content["outcome"]

            X.append(features)
            T.append([treatment_val])
            Y.append(outcome_val)

        if len(Y) < 20:
            return {"status": "insufficient_data_after_filtering", "n": len(Y)}

        X = np.array(X)
        T = np.array(T).ravel()
        Y = np.array(Y)

        if ECONML_AVAILABLE:
            try:
                model = LinearDML(
                    model_y="auto",
                    model_t="auto",
                    discrete_treatment=False,
                    random_state=42,
                )
                model.fit(Y, T, X=X)
                ate = model.ate(X)
                return {
                    "status": "success",
                    "method": "LinearDML",
                    "ate": float(ate),
                    "n_samples": len(Y),
                    "treatment": treatment_key,
                }
            except Exception as e:
                pass  # fall through to simple method

        # Fallback: simple residual-on-residual (Double ML style)
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import cross_val_predict

        mu_y = cross_val_predict(Ridge(), X, Y, cv=5)
        mu_t = cross_val_predict(Ridge(), X, T, cv=5)

        residual_y = Y - mu_y
        residual_t = T - mu_t

        ate = np.mean(residual_y * residual_t) / (np.var(residual_t) + 1e-8)

        return {
            "status": "success",
            "method": "simple_residual_on_residual",
            "ate": float(ate),
            "n_samples": len(Y),
            "treatment": treatment_key,
        }

    def get_best_priors(self, challenge_id: str) -> Dict[str, Any]:
        """
        Return the best known priors (loss weights, scoring expressions, etc.)
        for a given challenge, combining causal estimates and symbolic artifacts.
        """
        # Load recent PySR scoring expressions
        scoring_artifacts = load_symbolic_artifacts(
            artifact_type="pysr_scoring",
            challenge_id=challenge_id,
            limit=10,
        )

        # Load recent evolved loss weights
        weight_artifacts = load_symbolic_artifacts(
            artifact_type="evolved_loss_weights",
            challenge_id=challenge_id,
            limit=10,
        )

        best = {
            "challenge_id": challenge_id,
            "causal_estimates": self.causal_estimates.get(challenge_id, {}),
            "pysr_scoring": scoring_artifacts[:3] if scoring_artifacts else [],
            "evolved_weights": weight_artifacts[:3] if weight_artifacts else [],
        }

        return best

    def update_from_observations(self, challenge_id: str):
        """Re-estimate causal effects after new observations are added."""
        result = self.estimate_causal_effects(challenge_id)
        if result.get("status") == "success":
            self.causal_estimates[challenge_id] = result
            save_symbolic_artifact(
                artifact_type="causal_estimate",
                challenge_id=challenge_id,
                content=result,
                metadata={"source": "CausalKnowledgeBase"},
            )
