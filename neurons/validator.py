"""Hydrogen Validator Neuron (with real forward loop).

The validator now queries miners using the protocol, collects strategies,
validates them with PhysicsNeMo + physics gates, and scores them.
"""

import time
import bittensor as bt

from hydrogen.base.validator import BaseValidatorNeuron
from hydrogen.protocol import StrategySynapse
from hydrogen.challenges.poisson_2d import load_challenge
from hydrogen.physics.gates import evaluate_all_gates, compute_relative_l2_error
from hydrogen.training.physicsnemo_trainer import train_physics_neural_operator


class Validator(BaseValidatorNeuron):
    """
    Hydrogen Validator with real querying and scoring logic.
    """

    def __init__(self, config=None):
        super().__init__(config=config)
        bt.logging.info("Hydrogen Validator initialized with active forward loop.")

    async def forward(self):
        """
        Main validation loop.

        1. Pick an active challenge
        2. Query miners for strategies using StrategySynapse
        3. Validate each strategy (training + physics gates)
        4. Score and log results
        """
        bt.logging.info("Starting validation round...")

        challenge_id = "poisson_2d_v1"  # TODO: Make dynamic / multi-challenge

        # Get axons to query (sample of miners)
        # For simplicity we query all axons in metagraph for now
        axons = [axon for axon in self.metagraph.axons if axon.hotkey != self.wallet.hotkey.ss58_address]

        if not axons:
            bt.logging.warning("No miners found to query.")
            return

        bt.logging.info(f"Querying {len(axons)} miners for challenge {challenge_id}...")

        # Create synapse
        synapse = StrategySynapse(challenge_id=challenge_id)

        # Query miners
        responses = await self.dendrite(
            axons=axons,
            synapse=synapse,
            timeout=30,
        )

        results = []

        for response in responses:
            if response is None or not response.accepted:
                continue

            strategy = response.strategy
            if strategy is None:
                continue

            # Validate the strategy
            validation_result = self.validate_submission(challenge_id, strategy)

            results.append({
                "hotkey": response.dendrite.hotkey if response.dendrite else "unknown",
                "strategy": strategy,
                "validation": validation_result,
            })

            bt.logging.info(
                f"Miner {response.dendrite.hotkey[:8] if response.dendrite else '??'}: "
                f"score={validation_result.get('score', 0):.4f}, "
                f"hard_pass={validation_result.get('hard_pass', False)}"
            )

        bt.logging.info(f"Validation round complete. {len(results)} valid responses processed.")
        # TODO: Send results to Landscape, set weights, etc.

    def validate_submission(self, challenge_id: str, strategy: dict):
        """
        Core validation logic: runs short training + physics gates.
        """
        challenge = load_challenge(challenge_id)
        baseline_error = challenge.baseline_error

        # Run short training
        results = train_physics_neural_operator(challenge, strategy, epochs=6)

        # Evaluate gates
        hard_pass, gate_details = evaluate_all_gates(results, pde_type="poisson")

        if not hard_pass:
            return {
                "score": 0.0,
                "improvement": 0.0,
                "hard_pass": False,
                "gate_details": gate_details,
            }

        # Compute improvement
        u_pred = results["u_pred"]
        u_true = challenge.stress_data["u_true"][0]
        submission_error = compute_relative_l2_error(u_pred, u_true)
        improvement = float(torch.log(torch.tensor(baseline_error)) - torch.log(torch.tensor(submission_error)))

        score = max(0.0, improvement)

        return {
            "score": score,
            "improvement": improvement,
            "hard_pass": True,
            "gate_details": gate_details,
            "submission_error": submission_error,
        }


if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Hydrogen Validator running...")
            time.sleep(30)
