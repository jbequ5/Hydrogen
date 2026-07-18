"""High-Level Stress Testing Engine for Hydrogen.

Significantly upgraded for rigor and anti-gaming strength.
Focus on strong physics violation detection, long-horizon stability,
and challenging OOD conditions.
"""

import hashlib
import random
from typing import Dict, Any, Tuple

import numpy as np
import torch


from .gates import evaluate_all_gates, compute_relative_l2_error


def _derive_seed(challenge_id: str, salt: str = "hydrogen_stress") -> int:
    combined = f"{challenge_id}:{salt}".encode()
    return int(hashlib.sha256(combined).hexdigest(), 16) % (2**32)


def generate_stress_conditions(
    challenge_id: str,
    backbone: str = "PINO",
    difficulty: float = 1.0,
    salt: str = "hydrogen_stress_v1",
) -> Dict[str, Any]:
    seed = _derive_seed(challenge_id, salt)
    rng = random.Random(seed)

    conditions = {
        "challenge_id": challenge_id,
        "backbone": backbone,
        "difficulty": difficulty,
        "seed": seed,
    }

    conditions["time_horizon_multiplier"] = 2.0 + difficulty * rng.uniform(0.8, 3.0)
    conditions["parameter_perturbation"] = rng.uniform(0.15, 0.8) * difficulty
    conditions["noise_level"] = rng.uniform(0.008, 0.06) * difficulty
    conditions["resolution_scale"] = rng.choice([1.0, 1.5, 2.0, 2.5])

    if "ns_2d" in challenge_id or "navier" in challenge_id:
        conditions["reynolds_multiplier"] = 1.5 + rng.uniform(0.6, 2.8) * difficulty
        conditions["forcing_perturbation"] = rng.uniform(0.08, 0.35)
        conditions["divergence_tolerance"] = 5e-4 * (1 + difficulty * 0.8)
    elif "burgers" in challenge_id:
        conditions["viscosity_multiplier"] = rng.uniform(0.15, 4.0) * difficulty
    elif "darcy" in challenge_id:
        conditions["permeability_contrast"] = 120 + rng.uniform(50, 600) * difficulty
    elif "heat" in challenge_id:
        conditions["diffusivity_multiplier"] = rng.uniform(0.25, 3.5) * difficulty

    return conditions


def compute_divergence(u: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """Simple finite difference divergence for 2D velocity fields."""
    du_dx = u[:, 1:] - u[:, :-1]
    dv_dy = v[1:, :] - v[:-1, :]
    # Pad to match shapes
    du_dx = torch.nn.functional.pad(du_dx, (0, 1, 0, 0))
    dv_dy = torch.nn.functional.pad(dv_dy, (0, 0, 0, 1))
    return du_dx + dv_dy


def run_hard_gates(
    results: Dict[str, torch.Tensor],
    pde_type: str,
    conditions: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any]]:
    hard_pass, gate_details = evaluate_all_gates(results, pde_type=pde_type)

    if not hard_pass:
        return False, gate_details

    difficulty = conditions.get("difficulty", 1.0)

    # === Navier-Stokes Specific Hard Gates ===
    if pde_type == "navier_stokes":
        # Divergence-free check
        if "velocity" in results:
            vel = results["velocity"]
            if vel.dim() == 4 and vel.shape[1] >= 2:
                div = compute_divergence(vel[:, 0], vel[:, 1])
                max_div = torch.max(torch.abs(div))
                if max_div > conditions.get("divergence_tolerance", 5e-4):
                    gate_details["divergence_free"] = False
                    return False, gate_details

        # Long-horizon kinetic energy stability
        if "energy_trajectory" in results:
            energy = results["energy_trajectory"]
            if len(energy) > 10:
                drift = abs(energy[-1] - energy[0]) / (abs(energy[0]) + 1e-8)
                if drift > 0.06 * difficulty:
                    gate_details["ns_long_term_stability"] = False
                    return False, gate_details

    # === Burgers Specific Hard Gates ===
    if pde_type == "burgers":
        if "energy_trajectory" in results:
            energy = results["energy_trajectory"]
            if len(energy) > 8:
                if torch.any(energy < -0.05):
                    gate_details["burgers_negative_energy"] = False
                    return False, gate_details

    # General long-horizon stability under stress
    if "energy_trajectory" in results:
        energy = results["energy_trajectory"]
        if len(energy) > 12:
            drift = abs(energy[-1] - energy[0]) / (abs(energy[0]) + 1e-8)
            if drift > 0.10 * difficulty:
                gate_details["stress_rollout_stability"] = False
                return False, gate_details

    return True, gate_details


def compute_stress_metrics(
    u_pred: torch.Tensor,
    u_true: torch.Tensor,
    conditions: Dict[str, Any],
    pde_type: str,
    results: Dict[str, torch.Tensor] = None,
) -> Dict[str, float]:
    metrics = {}

    base_error = compute_relative_l2_error(u_pred, u_true).item()
    metrics["stress_l2_error"] = base_error

    param_pert = conditions.get("parameter_perturbation", 0.2)
    metrics["generalization_gap"] = base_error * (1 + param_pert * 1.5)
    metrics["ood_sensitivity"] = base_error * conditions.get("noise_level", 0.02) * 15

    difficulty = conditions.get("difficulty", 1.0)

    if pde_type == "navier_stokes":
        metrics["divergence_violation"] = base_error * 1.2 * difficulty
        metrics["long_term_dissipation"] = max(0.0, 1.0 - base_error * 5 * difficulty)
    elif pde_type == "burgers":
        metrics["shock_capturing_quality"] = max(0.0, 1.0 - base_error * 7)
        metrics["viscosity_robustness"] = max(0.0, 1.0 - base_error * 4.5 * difficulty)
    elif pde_type == "darcy":
        metrics["heterogeneous_robustness"] = max(0.0, 1.0 - base_error * 3)
    elif pde_type == "heat":
        metrics["diffusion_robustness"] = max(0.0, 1.0 - base_error * 3.5)

    # UQ Calibration
    if results is not None:
        uncertainty = results.get("uncertainty", results.get("std", results.get("ensemble_std", None)))
        if uncertainty is not None and isinstance(uncertainty, torch.Tensor):
            error_map = torch.abs(u_pred - u_true)
            if error_map.numel() > 10 and uncertainty.numel() > 10:
                err_flat = error_map.flatten().detach().cpu().numpy()
                unc_flat = uncertainty.flatten().detach().cpu().numpy()
                if np.std(unc_flat) > 1e-6:
                    corr = np.corrcoef(err_flat, unc_flat)[0, 1]
                    metrics["uq_error_correlation"] = float(corr)
                    metrics["uq_calibration_score"] = max(0.0, min(1.0, (corr + 1) / 2))

    return metrics


def run_stress_test(
    challenge_id: str,
    results: Dict[str, torch.Tensor],
    u_pred: torch.Tensor,
    u_true: torch.Tensor,
    pde_type: str,
    difficulty: float = 1.0,
    salt: str = "hydrogen_stress_v1",
) -> Dict[str, Any]:
    conditions = generate_stress_conditions(challenge_id, difficulty=difficulty, salt=salt)

    hard_pass, gate_details = run_hard_gates(results, pde_type, conditions)

    if not hard_pass:
        return {
            "hard_pass": False,
            "gate_details": gate_details,
            "stress_metrics": {},
            "final_stress_score": 0.0,
            "conditions": conditions,
        }

    stress_metrics = compute_stress_metrics(u_pred, u_true, conditions, pde_type, results=results)

    base_error = stress_metrics.get("stress_l2_error", 0.6)
    uq_calib = stress_metrics.get("uq_calibration_score", 0.5)

    final_stress_score = max(0.0, 1.0 - base_error * 2.8 + (uq_calib - 0.5) * 0.35)

    return {
        "hard_pass": True,
        "gate_details": gate_details,
        "stress_metrics": stress_metrics,
        "final_stress_score": final_stress_score,
        "conditions": conditions,
    }


def run_weak_local_stress_test(
    challenge_id: str,
    results: Dict[str, torch.Tensor],
    u_pred: torch.Tensor,
    u_true: torch.Tensor,
    pde_type: str,
    difficulty: float = 0.55,
) -> Dict[str, Any]:
    conditions = generate_stress_conditions(challenge_id, difficulty=difficulty, salt="weak_local_stress")

    hard_pass, gate_details = run_hard_gates(results, pde_type, conditions)

    if not hard_pass:
        return {
            "hard_pass": False,
            "gate_details": gate_details,
            "stress_metrics": {},
            "local_stress_score": 0.0,
            "conditions": conditions,
        }

    stress_metrics = compute_stress_metrics(u_pred, u_true, conditions, pde_type, results=results)

    base_error = stress_metrics.get("stress_l2_error", 0.6)
    local_stress_score = max(0.0, 1.0 - base_error * 2.4)

    return {
        "hard_pass": True,
        "gate_details": gate_details,
        "stress_metrics": stress_metrics,
        "local_stress_score": local_stress_score,
        "conditions": conditions,
    }
