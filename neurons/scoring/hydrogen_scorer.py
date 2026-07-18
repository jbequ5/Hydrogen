"""HydrogenScorer with Multi-Objective Scoring

Computes multiple fine-grained metrics internally.
Collapses them into high-level objectives for scoring.
Exports rich data for the Landscape Agent.
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

        # Configurable high-level objective weights
        self.stress_weight = getattr(config, "stress_weight", 0.75)
        self.benchmark_weight = getattr(config, "benchmark_weight", 0.25)

    def score_strategy(self, uid: int, hotkey: str, strategy: dict) -> float:
        challenge_id = strategy.get("challenge_id") or self._get_default_challenge(uid)
        backbone = strategy.get("backbone", "physicsnemo_fno")

        plan = get_evaluation_plan(challenge_id, backbone)

        try:
            eval_result = self._evaluate(strategy, plan, backbone)

            # Use high-level objectives for final score
            high_level = eval_result["high_level_objectives"]
            final_score = (
                self.stress_weight * high_level["stress_physics"] +
                self.benchmark_weight * high_level["benchmark_accuracy"]
            )

            # Attach rich data for Landscape Agent
            eval_result["landscape_data"] = {
                "uid": uid,
                "hotkey": hotkey,
                "challenge_id": challenge_id,
                "backbone": backbone,
                "fine_grained_scores": eval_result["fine_grained_scores"],
                "high_level_objectives": high_level,
                "strategy": strategy,
            }

            return final_score

        except Exception as e:
            bt.logging.error(f"Scoring failed for uid {uid}: {e}")
            return 0.0

    def _evaluate(self, strategy: dict, plan: dict, backbone: str) -> Dict[str, Any]:
        model = get_model(backbone=backbone)

        # === Training ===
        train_result = train_model(
            model=model,
            train_loader=plan.get("train_loader"),
            strategy=strategy,
            epochs=strategy.get("epochs", 50),
        )

        # === Stress + Physics ===
        stress_result = run_stress_test(
            challenge_id=plan.get("challenge_id", "unknown"),
            results=train_result,
            u_pred=train_result.get("u_pred"),
            u_true=plan.get("u_true"),
            pde_type=plan.get("pde_type", "generic"),
        )

        stress_physics_score = stress_result.get("final_stress_score", 0.0)

        # === Benchmark Accuracy ===
        benchmark_score = self._compute_benchmark_score(train_result, plan)

        # === Fine-grained scores (for Landscape) ===
        fine_grained = {
            "benchmark_mse": self._safe_get(train_result, "benchmark_mse", 0.0),
            "physics_residual": stress_result.get("physics_residual", 0.0),
            "long_term_stability": stress_result.get("long_term_stability", 0.0),
            "stress_generalization": stress_result.get("stress_generalization", 0.0),
        }

        # === High-level objectives (for scoring / Pareto) ===
        high_level = {
            "stress_physics": stress_physics_score,
            "benchmark_accuracy": benchmark_score,
            # Future: add "efficiency", "uncertainty_quality", etc.
        }

        return {
            "final_score": 0.0,  # Will be overwritten in score_strategy
            "fine_grained_scores": fine_grained,
            "high_level_objectives": high_level,
            "stress_result": stress_result,
            "train_result": train_result,
        }

    def _compute_benchmark_score(self, train_result: dict, plan: dict) -> float:
        try:
            benchmark_loader = plan.get("benchmark_loader")
            if not benchmark_loader:
                return 0.5

            model = train_result.get("model")
            if model is None:
                return 0.0

            total_error = 0.0
            count = 0
            for batch in benchmark_loader:
                x, y = batch[0], batch[1]
                with bt.no_grad():
                    pred = model(x)
                    error = bt.nn.functional.mse_loss(pred, y).item()
                    total_error += error
                    count += 1

            avg_error = total_error / max(count, 1)
            return max(0.0, 1.0 - avg_error * 5)

        except Exception:
            return 0.5

    def _safe_get(self, d: dict, key: str, default=0.0):
        return d.get(key, default) if isinstance(d, dict) else default

    def _get_default_challenge(self, uid: int) -> str:
        challenges = getattr(self.config, "active_challenges", ["poisson_2d_v1"])
        return challenges[uid % len(challenges)]
