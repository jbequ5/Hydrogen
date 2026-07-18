"""Evaluation Plan with anti-sandbagging adaptive difficulty."""

from typing import Dict, Any

import random

from hydrogen.data.benchmark_loader import get_benchmark_loader
from hydrogen.physics.stress import generate_stress_conditions


# Simple state to track recent performance per miner (in production use persistent storage)
RECENT_PERFORMANCE: Dict[str, float] = {}


def get_adaptive_difficulty(
    hotkey: str,
    base_difficulty: float = 1.0,
    alpha: float = 0.3,
    noise_level: float = 0.08,
) -> float:
    """
    Computes adaptive difficulty with anti-sandbagging measures:
    - Uses exponential moving average of performance
    - Adds noise
    - Applies conservative floor
    """
    prev = RECENT_PERFORMANCE.get(hotkey, 0.5)

    # Exponential moving average
    # (In real validator this would be updated after each validation)
    ema = alpha * prev + (1 - alpha) * base_difficulty

    # Add noise to prevent precise gaming
    noisy = ema + random.gauss(0, noise_level)

    # Conservative floor (difficulty can't go too low)
    final_diff = max(0.4, min(1.6, noisy))

    RECENT_PERFORMANCE[hotkey] = ema  # Update state
    return final_diff


def get_evaluation_plan(
    challenge_id: str,
    backbone: str,
    hotkey: str = "unknown",
    base_difficulty: float = 1.0,
) -> Dict[str, Any]:
    """
    Returns the full evaluation plan.
    """
    train_loader = get_benchmark_loader(challenge_id, split="train")

    # Adaptive difficulty with anti-sandbagging
    difficulty = get_adaptive_difficulty(hotkey, base_difficulty)

    stress_conditions = generate_stress_conditions(
        challenge_id=challenge_id,
        difficulty=difficulty,
    )

    benchmark_loader = get_benchmark_loader(challenge_id, split="test")

    return {
        "challenge_id": challenge_id,
        "backbone": backbone,
        "train_loader": train_loader,
        "stress_conditions": stress_conditions,
        "benchmark_loader": benchmark_loader,
        "adaptive_difficulty": difficulty,
    }
