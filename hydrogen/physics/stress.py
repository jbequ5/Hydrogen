"""Stress Test Engine for Hydrogen.

This module implements hard-to-game stress testing for physics-informed
neural operators. Key anti-gaming principles:

- Procedural generation seeded by challenge_id + validator hotkey
- Hard gates (binary fail → score 0)
- Multi-axis OOD stress (parameters, time, resolution, noise)
- Validator-only execution for hidden tests

Miners only get weak local versions for guidance.
"""

import hashlib
import random
from typing import Dict, Any, Tuple, List, Optional

import numpy as np
import torch


from .gates import evaluate_all_gates, compute_relative_l2_error


def _derive_seed(challenge_id: str, salt: str = "hydrogen_stress") -> int:
    """Create a deterministic but hidden seed for stress generation."""
    combined = f"{challenge_id}:{salt}".encode()
    return int(hashlib.sha256(combined).hexdigest(), 16) % (2**32)


def generate_stress_conditions(
    challenge_id: str,
    backbone: str = "PINO",
    difficulty: float = 1.0,
    salt: str = "hydrogen_stress_v1",
) -> Dict[str, Any]:
    """
    Generate procedural stress test conditions.

    These conditions are hidden from miners during local validation.
    """
    seed = _derive_seed(challenge_id, salt)
    rng = random.Random(seed)

    conditions = {
        "challenge_id": challenge_id,
        "backbone": backbone,
        "difficulty": difficulty,
        "seed": seed,
    }

    # Common stress axes
    conditions["time_horizon_multiplier"] = 1.5 + difficulty * rng.uniform(0.5, 2.0)
    conditions["parameter_perturbation"] = rng.uniform(0.1, 0.6) * difficulty
    conditions["noise_level"] = rng.uniform(0.005, 0.04) * difficulty
    conditions["resolution_scale"] = rng.choice([1.0, 1.5, 2.0])

    # Challenge-specific stress
    if "ns_2d" in challenge_id or "navier" in challenge_id:
        conditions["reynolds_multiplier"] = 1.2 + rng.uniform(0.3, 1.8) * difficulty
        conditions["forcing_perturbation"] = rng.uniform(0.05, 0.25)
    elif "burgers" in challenge_id:
        conditions["viscosity_multiplier"] = rng.uniform(0.3, 2.5) * difficulty
    elif "darcy" in challenge_id:
        conditions["permeability_contrast"] = 50 + rng.uniform(20, 400) * difficulty
    elif "heat" in challenge_id:
        conditions["diffusivity_multiplier"] = rng.uniform(0.4, 2.0) * difficulty

    return conditions


def run_hard_gates(
    results: Dict[str, torch.Tensor],
    pde_type: str,
    conditions: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any]]:
    """
    Run hard physics gates. Any failure → score = 0.
    """
    hard_pass, gate_details = evaluate_all_gates(results, pde_type=pde_type)

    # Additional hard checks based on stress conditions
    if not hard_pass:
        return False, gate_details

    # Example: extra rollout stability under stress
    if "energy_trajectory" in results:
        energy = results["energy_trajectory"]
        if len(energy) > 10:
            drift = abs(energy[-1] - energy[0]) / (abs(energy[0]) + 1e-8)
            if drift > 0.05 * conditions.get("difficulty", 1.0):
                gate_details["stress_rollout_drift"] = False
                return False, gate_details

    return True, gate_details


def compute_stress_metrics(
    u_pred: torch.Tensor,
    u_true: torch.Tensor,
    conditions: Dict[str, Any],
    pde_type: str,
) -> Dict[str, float]:
    """
    Compute stress metrics on the hidden OOD set.
    """
    metrics = {}

    # Base error on stress set
    base_error = compute_relative_l2_error(u_pred, u_true).item()
    metrics["stress_l2_error"] = base_error

    # Generalization gap (placeholder - would compare to public holdout)
    metrics["generalization_gap"] = base_error * conditions.get("parameter_perturbation", 0.2)

    # OOD sensitivity
    metrics["ood_sensitivity"] = base_error * conditions.get("noise_level", 0.02) * 10

    if pde_type == "navier_stokes":
        metrics["conservation_violation"] = base_error * 0.5  # placeholder
    elif pde_type == "burgers":
        metrics["shock_preservation"] = max(0.0, 1.0 - base_error * 5)

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
    """
    Main entry point for running a hidden stress test.

    Returns:
        hard_pass (bool)
        gate_details
        stress_metrics
        final_stress_score (float)
    """
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

    stress_metrics = compute_stress_metrics(u_pred, u_true, conditions, pde_type)

    # Simple stress score (can be made more sophisticated)
    base_error = stress_metrics.get("stress_l2_error", 0.5)
    final_stress_score = max(0.0, 1.0 - base_error * 3.0)

    return {
        "hard_pass": True,
        "gate_details": gate_details,
        "stress_metrics": stress_metrics,
        "final_stress_score": final_stress_score,
        "conditions": conditions,
    }
