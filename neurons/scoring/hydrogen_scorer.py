"""HydrogenScorer

Bridges the validator loop with our core evaluation logic.
Supports multiple challenges and multiple backbones.
"""

from typing import Dict, Any

import bittensor as bt

from hydrogen.evaluation.plan import get_evaluation_plan
from hydrogen.training.trainer import train_model
from hydrogen.physics.stress import run_stress_test


class HydrogenScorer:
    def __init__(self, config: bt.config):
        self.config = config

    def score_strategy(self, uid: int, hotkey: str, strategy: dict) -> float:
        """
        Main scoring entrypoint called by the validator.
        Returns a single float score.
        """
        challenge_id = strategy.get("challenge_id") or self._get_default_challenge(uid)
        backbone = strategy.get("backbone", "physicsnemo_fno")

        # Get train + stress evaluation plan
        plan = get_evaluation_plan(challenge_id, backbone)

        # Run training + stress testing
        eval_result = self._evaluate(strategy, plan, backbone)

        return eval_result.get("final_score", 0.0)

    def _evaluate(self, strategy: dict, plan: dict, backbone: str) -> Dict[str, Any]:
        # 1. Training
        train_result = train_model(
            model=None,  # get_model is called inside train_model via backbone
            train_loader=plan.get("train_loader"),
            strategy=strategy,
            epochs=strategy.get("epochs", 50),
        )

        # 2. Stress Testing + Physics Gates
        stress_result = run_stress_test(
            challenge_id=plan.get("challenge_id", "unknown"),
            results=train_result,
            u_pred=train_result.get("u_pred"),
            u_true=plan.get("u_true"),
            pde_type=plan.get("pde_type", "generic"),
        )

        final_score = stress_result.get("final_stress_score", 0.0)

        return {
            "final_score": final_score,
            "stress_result": stress_result,
            "train_result": train_result,
        }

    def _get_default_challenge(self, uid: int) -> str:
        challenges = getattr(self.config, "active_challenges", ["poisson_2d_v1"])
        return challenges[uid % len(challenges)]
