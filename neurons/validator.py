"""Hydrogen Validator with sophisticated per-challenge aware weight setting.

Weights are now more aligned with the spec: top performers on challenges
get stronger influence, and only miners beating baseline contribute meaningfully.
"""

import time
import numpy as np
import bittensor as bt

from hydrogen.base.validator import BaseValidatorNeuron
from hydrogen.protocol import StrategySynapse


class Validator(BaseValidatorNeuron):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.scores = {}           # hotkey -> moving average score
        self.challenge_history = {}  # hotkey -> list of recent improvements
        self.moving_average_alpha = 0.15
        bt.logging.info("Hydrogen Validator initialized with per-challenge aware weighting.")

    async def forward(self):
        bt.logging.info("Starting validation round...")

        challenge_id = "poisson_2d_v1"

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

                bt.logging.info(f"{hotkey[:8]}: score={score:.4f}, improvement={improvement:+.4f}")

        # Update scores with per-challenge awareness
        self._update_scores(round_scores, improvements)

        if self.scores:
            self._set_weights()

    def _update_scores(self, round_scores: dict, improvements: list):
        """Update scores with emphasis on recent strong challenge performance."""
        for hotkey, score in round_scores.items():
            if hotkey in self.scores:
                self.scores[hotkey] = (
                    (1 - self.moving_average_alpha) * self.scores[hotkey] +
                    self.moving_average_alpha * score
                )
            else:
                self.scores[hotkey] = score

        # Bonus for top performers this round (closer to spec's top-4 emphasis)
        if improvements:
            sorted_improvements = sorted(improvements, key=lambda x: x[1], reverse=True)
            top_k = sorted_improvements[:4]  # Top 4 get extra weight influence

            for hotkey, improvement in top_k:
                if improvement > 0:  # Only reward those who beat baseline
                    if hotkey in self.scores:
                        self.scores[hotkey] *= 1.15  # Boost top performers

    def _set_weights(self):
        """Set weights with bias toward consistent + recent top performers."""
        try:
            hotkeys = []
            weights = []

            for hotkey, score in self.scores.items():
                if hotkey in self.metagraph.hotkeys:
                    uid = self.metagraph.hotkeys.index(hotkey)
                    hotkeys.append(uid)
                    # Only give meaningful weight to miners who have shown positive improvement
                    weights.append(max(0.01, score))

            if not hotkeys:
                return

            weights = np.array(weights, dtype=np.float32)
            weights = weights / weights.sum()

            result = self.subtensor.set_weights(
                wallet=self.wallet,
                netuid=self.config.netuid,
                uids=hotkeys,
                weights=weights,
            )
            bt.logging.info(f"Weights set. Success={result}")

        except Exception as e:
            bt.logging.error(f"Weight setting failed: {e}")

    def validate_submission(self, challenge_id: str, strategy: dict):
        from hydrogen.challenges.poisson_2d import load_challenge
        from hydrogen.physics.gates import evaluate_all_gates, compute_relative_l2_error
        from hydrogen.training.physicsnemo_trainer import train_physics_neural_operator

        challenge = load_challenge(challenge_id)
        baseline_error = challenge.baseline_error

        results = train_physics_neural_operator(challenge, strategy, epochs=6)
        hard_pass, gate_details = evaluate_all_gates(results, pde_type="poisson")

        if not hard_pass:
            return {"score": 0.0, "improvement": 0.0, "hard_pass": False}

        u_pred = results["u_pred"]
        u_true = challenge.stress_data["u_true"][0]
        submission_error = compute_relative_l2_error(u_pred, u_true)
        improvement = float(torch.log(torch.tensor(baseline_error)) - torch.log(torch.tensor(submission_error)))

        return {
            "score": max(0.0, improvement),
            "improvement": improvement,
            "hard_pass": True,
            "gate_details": gate_details,
        }


if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Hydrogen Validator running...")
            time.sleep(30)
