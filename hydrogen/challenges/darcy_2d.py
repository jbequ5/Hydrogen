"""Darcy 2D Challenge (Phase 0 MVP) - Same rigor as Poisson.

Variable coefficient elliptic PDE: -∇·(k(x)∇u) = f
Common benchmark from PDEBench / PhysicsNeMo.

Provides train/holdout/stress splits + symbolic metadata.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import numpy as np
import torch


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


def get_symbolic_metadata() -> Dict[str, Any]:
    """Symbolic features for Darcy flow (variable permeability)."""
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


def generate_darcy_data(
    resolution: Tuple[int, int] = (128, 128),
    seed: int = 42,
    n_samples: int = 8,
    permeability_contrast: float = 100.0,
) -> Dict[str, torch.Tensor]:
    """
    Generate Darcy flow data with heterogeneous permeability.

    Simple model: k(x) = 1 + contrast * random_field
    Solution u satisfies the elliptic equation.
    In production: use PhysicsNeMo or FEniCS reference solutions.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    nx, ny = resolution
    x = torch.linspace(0, 1, nx)
    y = torch.linspace(0, 1, ny)
    X, Y = torch.meshgrid(x, y, indexing="ij")

    # Simple heterogeneous permeability field
    k = 1.0 + permeability_contrast * torch.rand(nx, ny)

    # Manufactured solution (smooth)
    u_true = torch.sin(np.pi * X) * torch.sin(np.pi * Y) * (1 + 0.1 * torch.sin(2 * np.pi * X * Y))

    # Forcing term (approximate)
    f = torch.ones_like(u_true) * 0.1

    # Add noise for variety
    u_noisy = u_true + 0.03 * torch.randn_like(u_true)

    return {
        "x": X.unsqueeze(0).repeat(n_samples, 1, 1),
        "y": Y.unsqueeze(0).repeat(n_samples, 1, 1),
        "u_true": u_true.unsqueeze(0).repeat(n_samples, 1, 1),
        "f": f.unsqueeze(0).repeat(n_samples, 1, 1),
        "k": k.unsqueeze(0).repeat(n_samples, 1, 1),
        "u_noisy": u_noisy.unsqueeze(0).repeat(n_samples, 1, 1),
    }


def load_challenge(challenge_id: str = "darcy_2d_v1") -> Challenge:
    if challenge_id != "darcy_2d_v1":
        raise ValueError(f"Unknown challenge: {challenge_id}")

    resolution = (128, 128)
    full_data = generate_darcy_data(resolution=resolution, n_samples=8)

    train_data = {k: v[:4] for k, v in full_data.items()}
    holdout_data = {k: v[4:6] for k, v in full_data.items()}
    stress_data = {k: v[6:8] for k, v in full_data.items()}

    baseline_error = 0.095  # Slightly harder than Poisson

    return Challenge(
        challenge_id=challenge_id,
        problem="darcy",
        dim=2,
        resolution=resolution,
        train_data=train_data,
        holdout_data=holdout_data,
        stress_data=stress_data,
        symbolic_metadata=get_symbolic_metadata(),
        baseline_error=baseline_error,
    )


def get_baseline_error(challenge_id: str = "darcy_2d_v1") -> float:
    return load_challenge(challenge_id).baseline_error
