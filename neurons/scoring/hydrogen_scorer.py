"""HydrogenScorer with 3 High-Level Objectives (45/30/25)

Physics Fidelity : 45%
Robustness       : 30%
Accuracy         : 25%

Expanded fine-grained metrics for rich Landscape data.
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

        # 45/30/25 weighting
        self.physics_weight = getattr(config, "physics_weight", 0.45)
        self.robustness_weight = getattr(config, "robustness_weight", 0.30)
        self.accuracy_weight = getattr(config, "accuracy_weight", 0.25)

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

        # === Expanded fine-grained metrics ===
        fine_grained = {
            # Accuracy metrics
            "benchmark_mse": self._safe_get(train_result, "benchmark_mse", 0.0),
            "relative_l2_error": stress_result.get("relative_l2_error", 0.0),
            "max_error": stress_result.get("max_error", 0.0),

            # Physics fidelity metrics
            "physics_residual": stress_result.get("physics_residual", 0.0),
            "divergence_error": stress_result.get("divergence_error", 0.0),
            "energy_stability": stress_result.get("energy_stability", 0.0),
            "boundary_violation": stress_result.get("boundary_violation", 0.0),
            "conservation_error": stress_result.get("conservation_error", 0.0),

            # Robustness metrics
            "long_term_stability": stress_result.get("long_term_stability", 0.0),
            "stress_generalization": stress_result.get("stress_generalization", 0.0),
            "parameter_sensitivity": stress_result.get("parameter_sensitivity", 0.0),
            "noise_robustness": stress_result.get("noise_robustness", 0.0),
        }

        # === 3 High-level objectives ===
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
        residual = 1.0 - min(1.0, fine.get("physics_residual", 0.5))
        divergence = 1.0 - min(1.0, fine.get("divergence_error", 0.5))
        energy = fine.get("energy_stability", 0.5)
        boundary = 1.0 - min(1.0, fine.get("boundary_violation", 0.5))
        conservation = 1.0 - min(1.0, fine.get("conservation_error", 0.5))
        return (residual + divergence + energy + boundary + conservation) / 5.0

    def _compute_robustness(self, fine: dict) -> float:
        stability = fine.get("long_term_stability", 0.5)
        generalization = fine.get("stress_generalization", 0.5)
        sensitivity = 1.0 - min(1.0, fine.get("parameter_sensitivity", 0.5))
        noise_rob = fine.get("noise_robustness", 0.5)
        return (stability + generalization + sensitivity + noise_rob) / 4.0

    def _compute_accuracy(self, fine: dict) -> float:
        rel_l2 = 1.0 - min(1.0, fine.get("relative_l2_error", 0.5))
        max_err = 1.0 - min(1.0, fine.get("max_error", 0.5))
        mse_score = max(0.0, 1.0 - fine.get("benchmark_mse", 0.5) * 5)
        return (rel_l2 + max_err + mse_score) / 3.0

    def _safe_get(self, d: dict, key: str, default=0.0):
        return d.get(key, default) if isinstance(d, dict) else default

    def _get_default_challenge(self, uid: int) -> str:
        challenges = getattr(self.config, "active_challenges", ["poisson_2d_v1"])
        return challenges[uid % len(challenges)]
