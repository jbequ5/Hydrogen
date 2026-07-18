"""Hydrogen Validator with proper ground truth (u_true) handling."""

import time
import numpy as np
import torch
import bittensor as bt

from hydrogen.base.validator import BaseValidatorNeuron
from hydrogen.protocol import StrategySynapse
from hydrogen.challenges import load_challenge
from hydrogen.physics.stress import run_stress_test
from hydrogen.training.physicsnemo_trainer import train_physics_neural_operator
from hydrogen.evaluation.plan import get_evaluation_plan


def get_ground_truth_batch(challenge_id: str, batch_size: int = 4):
    """Load a small batch of real ground truth from benchmark test split."""
    from hydrogen.data.benchmark_loader import get_benchmark_loader
    try:
        loader = get_benchmark_loader(challenge_id, split="test", batch_size=batch_size)
        x, y = next(iter(loader))
        return y[:batch_size]
    except Exception:
        return torch.zeros(batch_size, 1, 64, 64)


class Validator(BaseValidatorNeuron):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.scores = {}
        self.moving_average_alpha = 0.15
        self.current_challenge_index = 0
        self.challenge_ids = [
            "poisson_2d_v1",
            "darcy_2d_v1",
            "burgers_v1",
            "heat_v1",
            "elasticity_2d_v1",
            "ns_2d_laminar_v1",
        ]
        self.use_benchmark = True
        bt.logging.info("Hydrogen Validator with proper ground truth handling.")

    async def forward(self):
        bt.logging.info("Starting validation round...")

        challenge_id = self.challenge_ids[self.current_challenge_index]
        self.current_challenge_index = (self.current_challenge_index + 1) % len(self.challenge_ids)

        axons = [a for a in self.metagraph.axons if a.hotkey != self.wallet.hotkey.ss58_address]
        if not axons:
            return

        synapse = StrategySynapse(challenge_id=challenge_id)
        responses = await self.dendrite(axons=axons, synapse=synapse, timeout=30)

        round_scores = {}
        improvements = []

        for response in responses:
            if not response or not getattr(response, "accepted", False):
                continue
            strategy = getattr(response, "strategy", None)
            if not strategy:
                continue

            validation = self.validate_submission(challenge_id, strategy)
            hotkey = response.dendrite.hotkey if response.dendrite else None

            if hotkey and validation.get("hard_pass"):
                score = validation["score"]
                improvement = validation.get("improvement", 0.0)
                round_scores[hotkey] = score
                improvements.append((hotkey, improvement))

        self._update_scores(round_scores, improvements)

        if self.scores:
            self._set_weights()

    def _update_scores(self, round_scores: dict, improvements: list):
        for hotkey, score in round_scores.items():
            if hotkey in self.scores:
                self.scores[hotkey] = (1 - self.moving_average_alpha) * self.scores[hotkey] + self.moving_average_alpha * score
            else:
                self.scores[hotkey] = score

        if improvements:
            sorted_improvements = sorted(improvements, key=lambda x: x[1], reverse=True)
            top_k = sorted_improvements[:4]
            for hotkey, improvement in top_k:
                if improvement > 0 and hotkey in self.scores:
                    self.scores[hotkey] *= 1.15

    def _set_weights(self):
        try:
            hotkeys = []
            weights = []
            for hotkey, score in self.scores.items():
                if hotkey in self.metagraph.hotkeys:
                    uid = self.metagraph.hotkeys.index(hotkey)
                    hotkeys.append(uid)
                    weights.append(max(0.01, score))

            if not hotkeys:
                return

            weights = np.array(weights, dtype=np.float32)
            weights = weights / weights.sum()

            self.subtensor.set_weights(
                wallet=self.wallet,
                netuid=self.config.netuid,
                uids=hotkeys,
                weights=weights,
            )

        except Exception as e:
            bt.logging.error(f"Weight setting failed: {e}")

    def validate_submission(self, challenge_id: str, strategy: dict):
        backbone = strategy.get("backbone", "physicsnemo_fno")

        plan = get_evaluation_plan(challenge_id, backbone)

        results = train_physics_neural_operator(challenge_id, strategy, epochs=6)

        # Get real ground truth for stress testing
        u_true = get_ground_truth_batch(challenge_id, batch_size=4)

        stress_result = run_stress_test(
            challenge_id=challenge_id,
            results=results,
            u_pred=results.get("u_pred", torch.zeros(1, 1, 64, 64)),
            u_true=u_true,
            pde_type=challenge_id.split("_")[0],
            difficulty=plan["adaptive_difficulty"],
        )

        if not stress_result["hard_pass"]:
            return {
                "score": 0.0,
                "improvement": 0.0,
                "hard_pass": False,
                "stress_result": stress_result,
            }

        stress_score = stress_result.get("final_stress_score", 0.5)

        final_score = stress_score

        return {
            "score": max(0.0, final_score),
            "improvement": 0.0,
            "hard_pass": True,
            "stress_result": stress_result,
            "backbone_used": backbone,
        }


if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Hydrogen Validator running...")
            time.sleep(30)
