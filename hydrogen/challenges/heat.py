"""Heat Challenge (Phase 0) - Transient diffusion.

ρu/ρt = α ∇^{2}u

Parabolic PDE. Good test for rollout stability and energy dissipation.
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
        "governing_pde": "ρu/ρt = α ∇^{2}u",
        "symmetries": ["translation"],
        "conservation_laws": ["energy"],
        "dimensionless_groups": {"Fourier_number": "moderate"},
        "boundary_types": ["dirichlet", "neumann"],
        "suggested_loss_weights": {
            "pde_residual": 1.0,
            "diffusion": 1.2,
            "boundary": 0.7,
        },
        "validity_domain": {"diffusivity": [0.01, 1.0]},
        "hard_constraints": ["diffusion"],
    }


def generate_heat_data(
    resolution: Tuple[int, int] = (128, 64),
    seed: int = 42,
    n_samples: int = 6,
    diffusivity: float = 0.1,
) -> Dict[str, torch.Tensor]:
    torch.manual_seed(seed)
    np.random.seed(seed)

    nx, nt = resolution
    x = torch.linspace(0, 1, nx)
    t = torch.linspace(0, 1, nt)
    X, T = torch.meshgrid(x, t, indexing="ij")

    # Initial Gaussian-like condition
    u0 = torch.exp(-((x - 0.5)**2) / 0.05)

    u = torch.zeros(nx, nt)
    u[:, 0] = u0

    dx = x[1] - x[0]
    dt = t[1] - t[0]

    for n in range(nt - 1):
        u_xx = (torch.roll(u[:, n], -1) - 2 * u[:, n] + torch.roll(u[:, n], 1)) / dx**2
        u[:, n + 1] = u[:, n] + diffusivity * dt * u_xx

    u_noisy = u + 0.015 * torch.randn_like(u)

    return {
        "x": X.unsqueeze(0).repeat(n_samples, 1, 1),
        "t": T.unsqueeze(0).repeat(n_samples, 1, 1),
        "u_true": u.unsqueeze(0).repeat(n_samples, 1, 1),
        "u_noisy": u_noisy.unsqueeze(0).repeat(n_samples, 1, 1),
        "diffusivity": torch.full((n_samples, 1, 1), diffusivity),
    }


def load_challenge(challenge_id: str = "heat_v1") -> Challenge:
    if challenge_id != "heat_v1":
        raise ValueError(f"Unknown challenge: {challenge_id}")

    resolution = (128, 64)
    full_data = generate_heat_data(resolution=resolution, n_samples=6)

    train_data = {k: v[:3] for k, v in full_data.items()}
    holdout_data = {k: v[3:4] for k, v in full_data.items()}
    stress_data = {k: v[4:6] for k, v in full_data.items()}

    baseline_error = 0.09

    return Challenge(
        challenge_id=challenge_id,
        problem="heat",
        dim=1,
        resolution=resolution,
        train_data=train_data,
        holdout_data=holdout_data,
        stress_data=stress_data,
        symbolic_metadata=get_symbolic_metadata(),
        baseline_error=baseline_error,
    )


def get_baseline_error(challenge_id: str = "heat_v1") -> float:
    return load_challenge(challenge_id).baseline_error
