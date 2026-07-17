"""Hydrogen Miner - Improved robustness and intelligence."""

import time
import typing
import random
import bittensor as bt

from hydrogen.protocol import StrategySynapse
from hydrogen.base.miner import BaseMinerNeuron
from hydrogen.miner.strategy_generator import generate_strategy, get_local_validation_score


class Miner(BaseMinerNeuron):
    """
    Improved Hydrogen Miner with better local validation and robustness.
    """

    def __init__(self, config=None):
        super().__init__(config=config)
        self.local_validation_enabled = True
        bt.logging.info("Hydrogen Miner initialized (improved robustness).")

    async def forward(self, synapse: StrategySynapse) -> StrategySynapse:
        bt.logging.info(f"Received request for challenge: {synapse.challenge_id}")

        try:
            if synapse.strategy is None:
                # Generate strategy using symbolic metadata
                strategy = generate_strategy(synapse.challenge_id)

                # Perform local validation before responding
                if self.local_validation_enabled:
                    improvement, hard_pass, gate_details = get_local_validation_score(
                        synapse.challenge_id,
                        strategy,
                        use_real_training=True,
                        quick_epochs=5,
                    )

                    if hard_pass:
                        bt.logging.info(f"Local validation PASSED. Est. improvement: {improvement:+.4f}")
                        synapse.strategy = strategy
                        synapse.accepted = True
                        synapse.message = f"Validated locally (est. improvement {improvement:.3f})"
                    else:
                        bt.logging.warning("Local validation FAILED gates. Adjusting strategy...")
                        # Could implement strategy mutation here in the future
                        synapse.strategy = strategy
                        synapse.accepted = False
                        synapse.message = "Local validation failed - strategy may need tuning"
                else:
                    # No local validation
                    synapse.strategy = strategy
                    synapse.accepted = True
                    synapse.message = "Strategy generated (no local validation)"

            else:
                synapse.accepted = True
                synapse.message = "Strategy submission acknowledged"
                synapse.submission_id = f"sub_{int(time.time())}"

        except Exception as e:
            bt.logging.error(f"Error in miner forward: {e}")
            synapse.accepted = False
            synapse.message = f"Internal error: {str(e)}"

        return synapse

    async def blacklist(self, synapse: StrategySynapse) -> typing.Tuple[bool, str]:
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            return True, "Missing dendrite or hotkey"

        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            return True, "Unrecognized hotkey"

        return False, "Hotkey recognized"

    async def priority(self, synapse: StrategySynapse) -> float:
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            return 0.0
        try:
            uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
            return float(self.metagraph.S[uid])
        except Exception:
            return 0.0


if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Hydrogen Miner running...")
            time.sleep(10)
