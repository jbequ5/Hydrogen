"""Hydrogen Miner Neuron.

Follows the official Bittensor subnet template structure.
Inherits from BaseMinerNeuron (to be extracted into hydrogen/base/).

This miner is lightweight (no GPU required). It can:
- Respond to validator queries for strategies
- Submit strategies for open challenges (autonomous mode)
"""

import time
import typing
import bittensor as bt

from hydrogen.protocol import StrategySynapse, GetActiveChallengesSynapse

# TODO: Later import from hydrogen.base.miner import BaseMinerNeuron
# For now we use a minimal local base to match template style


class BaseMinerNeuron:
    """Minimal base to match template pattern until we extract hydrogen/base/"""

    def __init__(self, config=None):
        self.config = config or bt.config()
        self.wallet = bt.wallet(config=self.config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = self.subtensor.metagraph(self.config.netuid)
        self.axon = bt.axon(wallet=self.wallet, config=self.config)

        # Attach forward, blacklist, priority
        self.axon.attach(
            forward_fn=self.forward,
            blacklist_fn=self.blacklist,
            priority_fn=self.priority,
        )

    def sync(self):
        self.metagraph.sync(subtensor=self.subtensor)

    def run(self):
        self.sync()
        self.axon.serve(netuid=self.config.netuid, subtensor=self.subtensor)
        self.axon.start()

        bt.logging.info(f"Hydrogen Miner started on netuid {self.config.netuid}")

        try:
            while True:
                time.sleep(10)
                self.sync()
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Miner stopped.")


class Miner(BaseMinerNeuron):
    """
    Your Hydrogen miner implementation.
    """

    def __init__(self, config=None):
        super().__init__(config=config)
        bt.logging.info("Hydrogen Miner initialized.")

    async def forward(self, synapse: StrategySynapse) -> StrategySynapse:
        """
        Main logic for responding to strategy requests or submissions.
        """
        bt.logging.info(f"Received StrategySynapse for challenge: {synapse.challenge_id}")

        # TODO: Replace with real strategy generation logic
        # For now, return a dummy strategy
        if synapse.strategy is None:
            # Validator is asking for a strategy
            synapse.strategy = {
                "backbone": "PINO",
                "pino": {
                    "loss_vector": {"pde_residual": 1.0, "boundary": 0.8}
                },
                "epochs": 50,
            }
            synapse.accepted = True
            synapse.message = "Dummy strategy provided"
        else:
            # Miner is submitting a strategy
            synapse.accepted = True
            synapse.message = "Strategy received and accepted (demo)"
            synapse.submission_id = f"sub_{int(time.time())}"

        return synapse

    async def blacklist(self, synapse: StrategySynapse) -> typing.Tuple[bool, str]:
        """Basic blacklist logic."""
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            return True, "Missing dendrite or hotkey"

        # Allow only registered hotkeys for now
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            return True, "Unrecognized hotkey"

        return False, "Hotkey recognized"

    async def priority(self, synapse: StrategySynapse) -> float:
        """Priority based on stake (simple version)."""
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            return 0.0

        try:
            uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
            return float(self.metagraph.S[uid])
        except:
            return 0.0


if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Hydrogen Miner running...")
            time.sleep(10)
