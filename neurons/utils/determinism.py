# neurons/utils/determinism.py

"""
Centralized determinism utilities for Hydrogen.

Provides hierarchical, challenge-bound seeding and framework-level
controls for full pipeline reproducibility.

See docs/DETERMINISM_DESIGN.md for full specification.
"""

import hashlib
import os

from typing import Dict


import torch


def get_master_seed(challenge_id: str, validator_hotkey: str) -> int:
    """
    Derive a deterministic master seed from challenge and validator identity.
    """
    combined = f"{challenge_id}:{validator_hotkey}"
    return int(hashlib.sha256(combined.encode()).hexdigest(), 16) % (2**32)


def get_sub_seeds(master_seed: int) -> Dict[str, int]:
    """
    Generate a hierarchy of sub-seeds from the master seed.
    """
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
    """
    Apply all available PyTorch determinism flags.
    Note: This can reduce performance but is required for reproducibility.
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Also set environment variables for extra safety
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"


def get_jax_key(master_seed: int):
    """
    Return a JAX PRNG key from master seed (for JAX-based backbones).
    """
    try:
        import jax.numpy as jnp
        import jax.random as jrandom
        return jrandom.PRNGKey(master_seed)
    except ImportError:
        return None
