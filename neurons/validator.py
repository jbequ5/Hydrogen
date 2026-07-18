"""Hydrogen Validator

Main validator loop. Follows standard Bittensor patterns while integrating
our Hydrogen scoring system.
"""

import time

import bittensor as bt

from neurons.scoring.hydrogen_scorer import HydrogenScorer


class Validator:
    def __init__(self, config: bt.config):
        self.config = config
        self.subtensor = bt.subtensor(config)
        self.wallet = bt.wallet(config)
        self.metagraph = bt.metagraph(netuid=config.netuid)

        self.scorer = HydrogenScorer(config)
        self.active_challenges = getattr(config, "active_challenges", None) or [
            "poisson_2d_v1", "darcy_2d_v1", "burgers_v1"
        ]

    def run(self):
        bt.logging.info("Starting Hydrogen Validator...")

        while True:
            try:
                self.metagraph.sync()
                scores = self._evaluate_miners()

                if scores:
                    self._set_weights(scores)

            except Exception as e:
                bt.logging.error(f"Validator error: {e}")

            time.sleep(self.config.evaluation_interval)

    def _evaluate_miners(self) -> dict:
        scores = {}

        for uid in self.metagraph.uids:
            hotkey = self.metagraph.hotkeys[uid]
            strategy = self._get_strategy_for_uid(uid)

            if not strategy:
                scores[uid] = 0.0
                continue

            try:
                score = self.scorer.score_strategy(
                    uid=uid, hotkey=hotkey, strategy=strategy
                )
                scores[uid] = score
            except Exception as e:
                bt.logging.warning(f"Failed to score uid {uid}: {e}")
                scores[uid] = 0.0

        return scores

    def _set_weights(self, scores: dict):
        uids = list(scores.keys())
        weights = list(scores.values())

        weights_tensor = bt.tensor(weights, dtype=bt.float32)
        weights_tensor = weights_tensor / weights_tensor.sum()

        self.subtensor.set_weights(
            uids=uids,
            weights=weights_tensor,
            version_key=self.config.version_key,
            wait_for_finalization=True,
        )

    def _get_strategy_for_uid(self, uid: int) -> dict:
        # Placeholder - in production this would come from chain or off-chain store
        # For now returns a dummy strategy for testing
        return {
            "backbone": "physicsnemo_fno",
            "challenge_id": self.active_challenges[uid % len(self.active_challenges)],
            "epochs": 50,
        }


if __name__ == "__main__":
    config = bt.config()
    validator = Validator(config)
    validator.run()
