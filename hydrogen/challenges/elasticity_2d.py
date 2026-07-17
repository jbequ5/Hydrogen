"""Elasticity 2D Challenge (Phase 0) - Linear elasticity.

Vector PDE for displacement field. Introduces multi-component fields.

Simplified for MVP but follows same structure.
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
    return {
        "governing_pde": "∇·σ = f (linear elasticity)",
        "symmetries": ["translation", "rotation"],
        "conservation_laws": ["momentum"],
        "dimensionless_groups": {"Poisson_ratio": "typical"},
        "boundary_types": ["dirichlet", "neumann"],
        "suggested_loss_weights": {
            "pde_residual": 1.0,
            "strain_energy": 1.1,
            "boundary": 0.8,
        },
        "validity_domain": {"young_modulus": [1e3, 1e6]},
        "hard_constraints": ["linear_elasticity"],
    }


def generate_elasticity_data(
    resolution: Tuple[int, int] = (64, 64),
    seed: int = 42,
    n_samples: int = 4,
) -> Dict[str, torch.Tensor]:
    torch.manual_seed(seed)
    np.random.seed(seed)

    nx, ny = resolution
    x = torch.linspace(0, 1, nx)
    y = torch.linspace(0, 1, ny)
    X, Y = torch.meshgrid(x, y, indexing="ij")

    # Simple manufactured displacement field (ux, uy)
    ux = torch.sin(np.pi * X) * torch.cos(np.pi * Y) * 0.1
    uy = torch.cos(np.pi * X) * torch.sin(np.pi * Y) * 0.1

    # Add noise
    ux_noisy = ux + 0.01 * torch.randn_like(ux)
    uy_noisy = uy + 0.01 * torch.randn_like(uy)

    return {
        "x": X.unsqueeze(0).repeat(n_samples, 1, 1),
        "y": Y.unsqueeze(0).repeat(n_samples, 1, 1),
        "ux_true": ux.unsqueeze(0).repeat(n_samples, 1, 1),
        "uy_true": uy.unsqueeze(0).repeat(n_samples, 1, 1),
        "ux_noisy": ux_noisy.unsqueeze(0).repeat(n_samples, 1, 1),
        "uy_noisy": uy_noisy.unsqueeze(0).repeat(n_samples, 1, 1),
    }


def load_challenge(challenge_id: str = "elasticity_2d_v1") -> Challenge:
    if challenge_id != "elasticity_2d_v1":
        raise ValueError(f"Unknown challenge: {challenge_id}")

    resolution = (64, 64)
    full_data = generate_elasticity_data(resolution=resolution, n_samples=4)

    train_data = {k: v[:2] for k, v in full_data.items()}
    holdout_data = {k: v[2:3] for k, v in full_data.items()}
    stress_data = {k: v[3:4] for k, v in full_data.items()}

    baseline_error = 0.11

    return Challenge(
        challenge_id=challenge_id,
        problem="elasticity",
        dim=2,
        resolution=resolution,
        train_data=train_data,
        holdout_data=holdout_data,
        stress_data=stress_data,
        symbolic_metadata=get_symbolic_metadata(),
        baseline_error=baseline_error,
    )


def get_baseline_error(challenge_id: str = "elasticity_2d_v1") -> float:
    return load_challenge(challenge_id).baseline_error
