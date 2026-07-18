from collections import defaultdict
from typing import Dict, Optional, List

import bittensor as bt


class ChallengeWinnerTracker:
    """
    Tracks performance per challenge with exponential decay.
    Only miners who beat the current best *combined* score get strong credit.
    Supports participation dust and winner-heavy weight distribution.

    Designed to mimic Minos-style "round-only winner" behavior
    while supporting multiple challenges.
    """

    def __init__(self, decay_factor: float = 0.85):
        self.decay_factor = decay_factor

        # Per-challenge state
        self.best_combined_score: Dict[str, float] = {}
        self.current_leader: Dict[str, str] = {}

        # Per-miner state (with exponential decay)
        self.decayed_scores: Dict[str, float] = defaultdict(float)
        self.participation: Dict[str, int] = defaultdict(int)

        # Current round scores (reset every round)
        self.current_round_scores: Dict[str, float] = {}

    def update(self, hotkey: str, challenge_id: str, combined_score: float):
        """
        Update a miner's performance on a specific challenge.
        Only new combined bests get strong credit.
        """
        current_best = self.best_combined_score.get(challenge_id, 0.0)

        # Apply exponential decay to old performance
        self.decayed_scores[hotkey] *= self.decay_factor

        if combined_score > current_best:
            # New record on this challenge
            self.best_combined_score[challenge_id] = combined_score
            self.current_leader[challenge_id] = hotkey
            self.decayed_scores[hotkey] = combined_score
        else:
            # Still contribute, but much weaker
            self.decayed_scores[hotkey] += combined_score * (1 - self.decay_factor)

        self.participation[hotkey] += 1
        self.current_round_scores[hotkey] = combined_score

    def get_challenge_leader(self, challenge_id: str) -> Optional[str]:
        return self.current_leader.get(challenge_id)

    def reset_round(self):
        """Call this at the end of each round/day."""
        self.current_round_scores.clear()

    def get_weights(
        self,
        active_challenges: List[str],
        winner_weight: float = 0.65,
        dust_top_n: int = 8,
        dust_decay: float = 0.6,
    ) -> Dict[str, float]:
        """
        Returns a winner-heavy + participation dust weight distribution.
        Similar to Minos-style winner-heavy pruning dust logic.
        """
        weights: Dict[str, float] = {}
        total_weight = 0.0

        # Strong weight to current leaders of active challenges
        if active_challenges:
            per_challenge_leader_weight = winner_weight / len(active_challenges)
            for challenge_id in active_challenges:
                leader = self.current_leader.get(challenge_id)
                if leader:
                    weights[leader] = weights.get(leader, 0.0) + per_challenge_leader_weight
                    total_weight += per_challenge_leader_weight

        # Participation dust for recent miners
        sorted_participants = sorted(
            self.participation.items(),
            key=lambda x: x[1],
            reverse=True
        )[:dust_top_n]

        remaining_weight = 1.0 - total_weight
        for i, (hotkey, _) in enumerate(sorted_participants):
            dust_weight = remaining_weight * (dust_decay ** i)
            weights[hotkey] = weights.get(hotkey, 0.0) + dust_weight

        # Normalize
        total = sum(weights.values())
        if total > 0:
            for hotkey in list(weights.keys()):
                weights[hotkey] /= total

        return weights

    def get_stats(self) -> dict:
        return {
            "tracked_challenges": len(self.best_combined_score),
            "current_leaders": len(self.current_leader),
            "miners_tracked": len(self.decayed_scores),
        }
