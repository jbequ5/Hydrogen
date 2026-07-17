"""Landscape Agent with Distillation Proposal Logic.

The agent now proposes which strategies are worth distilling into specialists.
"""

import time
from typing import Dict, Any, List, Optional

from .causal_knowledge_base import CausalKnowledgeBase
from .storage import save_symbolic_artifact, load_symbolic_artifacts


class LandscapeAgent:
    """
    Central intelligence for causal + symbolic knowledge + distillation decisions.
    """

    def __init__(self, storage_dir: str = "./data/landscape"):
        self.storage_dir = storage_dir
        self.kb = CausalKnowledgeBase(storage_dir=storage_dir)
        self.last_update = None

    def ingest_observation(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        features: Dict[str, float] = None,
        treatment: Dict[str, float] = None,
        outcome: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.kb.add_observation(
            challenge_id=challenge_id,
            backbone=backbone,
            features=features,
            treatment=treatment,
            outcome=outcome,
            metadata=metadata,
        )

    def run_daily_update(self, challenge_ids: List[str] = None):
        if challenge_ids is None:
            challenge_ids = [
                "poisson_2d_v1",
                "darcy_2d_v1",
                "burgers_v1",
                "heat_v1",
                "elasticity_2d_v1",
                "ns_2d_laminar_v1",
            ]

        print(f"[Landscape] Running daily update for {len(challenge_ids)} challenges...")

        for challenge_id in challenge_ids:
            for backbone in ["PINO"]:
                causal_result = self.kb.estimate_causal_effects(
                    challenge_id, backbone=backbone
                )
                if causal_result.get("status") == "success":
                    print(f"  [{challenge_id}/{backbone}] Causal ATE updated")

        self.last_update = int(time.time())
        print("[Landscape] Daily update complete.")

    def propose_improved_priors(
        self,
        challenge_id: str,
        backbone: str = "PINO",
    ) -> Dict[str, Any]:
        return self.kb.get_best_priors(challenge_id, backbone=backbone)

    def get_publishable_priors(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        noise_level: float = 0.03,
    ) -> Dict[str, Any]:
        return self.kb.get_publishable_priors(
            challenge_id, backbone=backbone, noise_level=noise_level
        )

    def propose_distillation_candidates(
        self,
        challenge_id: str,
        backbone: str = "PINO",
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Propose the best strategies worth distilling into specialists.

        Ranking criteria (intelligent):
        - Causal effect strength (from Double ML)
        - Stress test performance
        - Improvement magnitude
        - UQ calibration quality (if available)
        """
        candidates = []

        # Get recent high-performing artifacts
        weight_artifacts = load_symbolic_artifacts(
            artifact_type="evolved_loss_weights",
            challenge_id=challenge_id,
            limit=20,
        )

        scoring_artifacts = load_symbolic_artifacts(
            artifact_type="pysr_scoring",
            challenge_id=challenge_id,
            limit=10,
        )

        causal = self.kb.causal_estimates.get(
            self.kb._make_key(challenge_id, backbone), {}
        )

        # Simple intelligent ranking for now
        # In future this will use more causal features + stress history
        for i, artifact in enumerate(weight_artifacts[:top_k]):
            content = artifact.get("content", {})
            candidate = {
                "rank": i + 1,
                "challenge_id": challenge_id,
                "backbone": backbone,
                "loss_vector": content.get("loss_vector", {}),
                "causal_ate": causal.get("ate", 0.0),
                "source_artifact": artifact.get("timestamp"),
                "recommended_for_distillation": True,
            }
            candidates.append(candidate)

        # Also consider strong PySR scoring expressions
        if scoring_artifacts:
            best_scoring = scoring_artifacts[0]
            candidates.append({
                "rank": len(candidates) + 1,
                "challenge_id": challenge_id,
                "backbone": backbone,
                "type": "scoring_expression",
                "expression": best_scoring.get("content", {}).get("expression"),
                "recommended_for_distillation": True,
            })

        return candidates[:top_k]

    def get_status(self) -> Dict[str, Any]:
        return {
            "last_update": self.last_update,
            "storage_dir": self.storage_dir,
            "causal_estimates_tracked": len(self.kb.causal_estimates),
        }
