# neurons/utils/determinism.py

"""
Centralized determinism utilities for Hydrogen.

Provides hierarchical, challenge-bound seeding and framework-level
controls for full pipeline reproducibility.
"""

import hashlib
import os
from typing import Dict, Optional

import torch


def get_master_seed(challenge_id: str, validator_hotkey: str) -> int:
    combined = f"{challenge_id}:{validator_hotkey}"
    return int(hashlib.sha256(combined.encode()).hexdigest(), 16) % (2**32)


def get_sub_seeds(master_seed: int) -> Dict[str, int]:
    def derive(name: str) -> int:
        return int(hashlib.sha256(f"{master_seed}:{name}".encode()).hexdigest(), 16) % (2**32)

    return {
        "data_loading": derive("data"),
        "augmentation": derive("aug"),
        "training": derive("train"),
        "stress_generation": derive("stress"),
        "noise": derive("noise"),
        "scoring": derive("scoring"),
    }


def setup_pytorch_determinism(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"


def get_jax_key(master_seed: int):
    try:
        import jax.random as jrandom
        return jrandom.PRNGKey(master_seed)
    except ImportError:
        return None


def get_data_loader_generator(seed: int) -> torch.Generator:
    """
    Returns a torch.Generator seeded for deterministic DataLoader shuffling.
    """
    g = torch.Generator()
    g.manual_seed(seed)
    return g


def setup_determinism_for_component(
    component: str, master_seed: int, sub_seeds: Optional[Dict[str, int]] = None
):
    """
    Convenience function to setup determinism for a specific component.
    """
    if sub_seeds is None:
        sub_seeds = get_sub_seeds(master_seed)

    seed = sub_seeds.get(component, master_seed)

    if component in ["data_loading", "augmentation", "training", "scoring"]:
        setup_pytorch_determinism(seed)

    return seed
