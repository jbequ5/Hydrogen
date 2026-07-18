"""HydrogenScorer with 3 High-Level Objectives

Fine-grained metrics collapsed into:
- Physics Fidelity
- Robustness
- Accuracy

Rich data exported for Landscape Agent.
"""

from typing import Dict, Any

import bittensor as bt

from hydrogen.backbones import get_model
from hydrogen.evaluation.plan import get_evaluation_plan
from hydrogen.training.trainer import train_model
from hydrogen.physics.stress import run_stress_test


class HydrogenScorer:
    def __init__(self, config: bt.config):
        self.config = config

        # Configurable weights for the 3 high-level objectives
        self.physics_weight = getattr(config, "physics_weight", 0.5)
        self.robustness_weight = getattr(config, "robustness_weight", 0.3)
        self.accuracy_weight = getattr(config, "accuracy_weight", 0.2)

    def score_strategy(self, uid: int, hotkey: str, strategy: dict) -> float:
        challenge_id = strategy.get("challenge_id") or self._get_default_challenge(uid)
        backbone = strategy.get("backbone", "physicsnemo_fno")

        plan = get_evaluation_plan(challenge_id, backbone)

        try:
            eval_result = self._evaluate(strategy, plan, backbone)

            high = eval_result["high_level_objectives"]
            final_score = (
                self.physics_weight * high["physics_fidelity"] +
                self.robustness_weight * high["robustness"] +
                self.accuracy_weight * high["accuracy"]
            )

            eval_result["landscape_data"] = {
                "uid": uid,
                "hotkey": hotkey,
                "challenge_id": challenge_id,
                "backbone": backbone,
                "fine_grained_scores": eval_result["fine_grained_scores"],
                "high_level_objectives": high,
                "strategy": strategy,
            }

            return final_score

        except Exception as e:
            bt.logging.error(f"Scoring failed for uid {uid}: {e}")
            return 0.0

    def _evaluate(self, strategy: dict, plan: dict, backbone: str) -> Dict[str, Any]:
        model = get_model(backbone=backbone)

        train_result = train_model(
            model=model,
            train_loader=plan.get("train_loader"),
            strategy=strategy,
            epochs=strategy.get("epochs", 50),
        )

        stress_result = run_stress_test(
            challenge_id=plan.get("challenge_id", "unknown"),
            results=train_result,
            u_pred=train_result.get("u_pred"),
            u_true=plan.get("u_true"),
            pde_type=plan.get("pde_type", "generic"),
        )

        # === Fine-grained scores ===
        fine_grained = {
            "benchmark_mse": self._safe_get(train_result, "benchmark_mse", 0.0),
            "physics_residual": stress_result.get("physics_residual", 0.0),
            "divergence_error": stress_result.get("divergence_error", 0.0),
            "energy_stability": stress_result.get("energy_stability", 0.0),
            "long_term_stability": stress_result.get("long_term_stability", 0.0),
            "stress_generalization": stress_result.get("stress_generalization", 0.0),
            "boundary_violation": stress_result.get("boundary_violation", 0.0),
        }

        # === High-level objectives (3) ===
        physics_fidelity = self._compute_physics_fidelity(fine_grained)
        robustness = self._compute_robustness(fine_grained)
        accuracy = self._compute_accuracy(fine_grained)

        high_level = {
            "physics_fidelity": physics_fidelity,
            "robustness": robustness,
            "accuracy": accuracy,
        }

        return {
            "final_score": 0.0,
            "fine_grained_scores": fine_grained,
            "high_level_objectives": high_level,
            "stress_result": stress_result,
            "train_result": train_result,
        }

    def _compute_physics_fidelity(self, fine: dict) -> float:
        # Combine physics-related fine-grained metrics
        residual = 1.0 - min(1.0, fine.get("physics_residual", 0.5))
        divergence = 1.0 - min(1.0, fine.get("divergence_error", 0.5))
        energy = fine.get("energy_stability", 0.5)
        boundary = 1.0 - min(1.0, fine.get("boundary_violation", 0.5))
        return (residual + divergence + energy + boundary) / 4.0

    def _compute_robustness(self, fine: dict) -> float:
        stability = fine.get("long_term_stability", 0.5)
        generalization = fine.get("stress_generalization", 0.5)
        return (stability + generalization) / 2.0

    def _compute_accuracy(self, fine: dict) -> float:
        return max(0.0, 1.0 - fine.get("benchmark_mse", 0.5) * 5)

    def _safe_get(self, d: dict, key: str, default=0.0):
        return d.get(key, default) if isinstance(d, dict) else default

    def _get_default_challenge(self, uid: int) -> str:
        challenges = getattr(self.config, "active_challenges", ["poisson_2d_v1"])
        return challenges[uid % len(challenges)]
