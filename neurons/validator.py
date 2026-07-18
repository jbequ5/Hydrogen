"""Hydrogen Validator with StrategyStore integration.

Uses ChallengeWinnerTracker + StrategyStore for clean strategy handling.
"""

import time

import bittensor as bt

from neurons.scoring.hydrogen_scorer import HydrogenScorer
from neurons.scoring.challenge_winner_tracker import ChallengeWinnerTracker
from neurons.strategy.strategy_store import LocalFileStrategyStore, StrategyStore


class Validator:
    def __init__(self, config: bt.config):
        self.config = config
        self.subtensor = bt.subtensor(config)
        self.wallet = bt.wallet(config)
        self.metagraph = bt.metagraph(netuid=config.netuid)

        self.scorer = HydrogenScorer(config)
        self.tracker = ChallengeWinnerTracker(decay_factor=0.85)

        # Strategy storage / retrieval
        self.strategy_store: StrategyStore = LocalFileStrategyStore(
            storage_dir=getattr(config, "strategy_storage_dir", "./strategies")
        )

        self.active_challenges = getattr(config, "active_challenges", None) or [
            "poisson_2d_v1", "darcy_2d_v1", "burgers_v1"
        ]
        self.dry_run = getattr(config, "dry_run", False)

        bt.logging.info(f"Hydrogen Validator initialized (Dry run: {self.dry_run})")

    def run(self):
        while True:
            try:
                self.metagraph.sync()
                self._evaluate_miners()

                if not self.dry_run:
                    self._set_weights()

                self._log_monitoring()

            except Exception as e:
                bt.logging.error(f"Validator error: {e}")

            time.sleep(self.config.evaluation_interval)

    def _evaluate_miners(self):
        for uid in self.metagraph.uids:
            hotkey = self.metagraph.hotkeys[uid]
            strategy = self.strategy_store.get_strategy(hotkey)

            if not strategy:
                continue

            try:
                result = self.scorer.score_strategy(uid, hotkey, strategy)

                challenge_id = strategy.get("challenge_id", "default")
                combined_score = result.get("combined_score", 0.0)

                self.tracker.update(hotkey, challenge_id, combined_score)

            except Exception as e:
                bt.logging.warning(f"Failed to score uid {uid} ({hotkey[:16]}...): {e}")

    def _set_weights(self):
        weights = self.tracker.get_weights(
            active_challenges=self.active_challenges,
            winner_weight=0.65,
            dust_top_n=8,
            dust_decay=0.6,
        )

        uids = []
        weight_values = []

        for hotkey, weight in weights.items():
            if hotkey in self.metagraph.hotkeys:
                uid = self.metagraph.hotkeys.index(hotkey)
                uids.append(uid)
                weight_values.append(weight)

        if not uids:
            bt.logging.warning("No valid hotkeys for weight submission")
            return

        total = sum(weight_values)
        if total > 0:
            weight_values = [w / total for w in weight_values]

        self.subtensor.set_weights(
            uids=uids,
            weights=weight_values,
            version_key=self.config.version_key,
            wait_for_finalization=True,
        )

        bt.logging.info(f"Weights submitted for {len(uids)} miners")

    def _log_monitoring(self):
        stats = self.tracker.get_stats()
        bt.logging.info(
            f"Challenges: {stats['tracked_challenges']} | "
            f"Leaders: {stats['current_leaders']} | "
            f"Miners: {stats['miners_tracked']}"
        )


if __name__ == "__main__":
    config = bt.config()
    validator = Validator(config)
    validator.run()
