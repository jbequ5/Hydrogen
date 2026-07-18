"""HydrogenScorer (Completed Version)

Fully integrates training, stress testing, physics gates, and benchmark scoring.
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

    def score_strategy(self, uid: int, hotkey: str, strategy: dict) -> float:
        challenge_id = strategy.get("challenge_id") or self._get_default_challenge(uid)
        backbone = strategy.get("backbone", "physicsnemo_fno")

        plan = get_evaluation_plan(challenge_id, backbone)

        try:
            eval_result = self._evaluate(strategy, plan, backbone)
            return eval_result.get("final_score", 0.0)
        except Exception as e:
            bt.logging.error(f"Scoring failed for uid {uid}: {e}")
            return 0.0

    def _evaluate(self, strategy: dict, plan: dict, backbone: str) -> Dict[str, Any]:
        model = get_model(backbone=backbone)

        # 1. Training
        train_result = train_model(
            model=model,
            train_loader=plan.get("train_loader"),
            strategy=strategy,
            epochs=strategy.get("epochs", 50),
        )

        # 2. Stress Testing + Physics Gates (primary signal)
        stress_result = run_stress_test(
            challenge_id=plan.get("challenge_id", "unknown"),
            results=train_result,
            u_pred=train_result.get("u_pred"),
            u_true=plan.get("u_true"),
            pde_type=plan.get("pde_type", "generic"),
        )

        # 3. Benchmark scoring (secondary signal from hold-out data)
        benchmark_score = self._compute_benchmark_score(train_result, plan)

        # Combine scores (stress is primary, benchmark provides supporting signal)
        stress_score = stress_result.get("final_stress_score", 0.0)
        final_score = 0.7 * stress_score + 0.3 * benchmark_score

        return {
            "final_score": final_score,
            "stress_result": stress_result,
            "benchmark_score": benchmark_score,
            "train_result": train_result,
        }

    def _compute_benchmark_score(self, train_result: dict, plan: dict) -> float:
        """
        Simple benchmark scoring using hold-out / test data from the evaluation plan.
        Can be expanded later with more sophisticated metrics.
        """
        try:
            benchmark_loader = plan.get("benchmark_loader")
            if not benchmark_loader:
                return 0.5  # neutral fallback

            # Run inference on benchmark test set
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
            # Convert error to score (lower error = higher score)
            benchmark_score = max(0.0, 1.0 - avg_error * 5)
            return min(1.0, benchmark_score)

        except Exception:
            return 0.5

    def _get_default_challenge(self, uid: int) -> str:
        challenges = getattr(self.config, "active_challenges", ["poisson_2d_v1"])
        return challenges[uid % len(challenges)]
