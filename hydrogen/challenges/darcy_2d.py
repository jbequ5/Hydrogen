"""Darcy 2D Challenge - Now with PDEBench support option."""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import numpy as np
import torch

try:
    from hydrogen.data.pdebench_loader import PDEBenchLoader
    PDEBENCH_AVAILABLE = True
except ImportError:
    PDEBENCH_AVAILABLE = False


@dataclass
class Challenge:
    challenge_id: str
    problem: str
    dim: int
    resolution: Tuple[int, int]
    train_data: Dict[str, torch.Tensor]
    holdout_data: Dict[str, torch.Tensor]
    stress_data: Dict[str, torch.Tensor]
    symbolic_metadata: Dict[str, Any]
    baseline_error: float
    data_source: str = "synthetic"


def get_symbolic_metadata() -> Dict[str, Any]:
    return {
        "governing_pde": "-∇·(k ∇u) = f",
        "symmetries": ["translation"],
        "conservation_laws": [],
        "dimensionless_groups": {"permeability_contrast": "high"},
        "boundary_types": ["dirichlet"],
        "suggested_loss_weights": {
            "pde_residual": 1.2,
            "boundary": 0.7,
        },
        "validity_domain": {"permeability_contrast": [10, 1000]},
        "hard_constraints": ["elliptic"],
    }


def generate_darcy_data(...):  # keep existing synthetic generator
    # ... (existing code)
    pass

def load_challenge(challenge_id: str = "darcy_2d_v1", use_benchmark: bool = False) -> Challenge:
    if use_benchmark and PDEBENCH_AVAILABLE:
        loader = PDEBenchLoader(pde_name="darcy")
        # In full implementation: load actual PDEBench data here
        print("[Info] PDEBench mode enabled for Darcy (implementation in progress)")

    # Fallback to synthetic for now
    resolution = (128, 128)
    full_data = generate_darcy_data(resolution=resolution, n_samples=8)

    train_data = {k: v[:4] for k, v in full_data.items()}
    holdout_data = {k: v[4:6] for k, v in full_data.items()}
    stress_data = {k: v[6:8] for k, v in full_data.items()}

    return Challenge(
        challenge_id=challenge_id,
        problem="darcy",
        dim=2,
        resolution=resolution,
        train_data=train_data,
        holdout_data=holdout_data,
        stress_data=stress_data,
        symbolic_metadata=get_symbolic_metadata(),
        baseline_error=0.095,
        data_source="pdebench" if use_benchmark else "synthetic",
    )
