"""Hydrogen Validator (Bittensor neuron - Phase 0 MVP, now with working forward).

Core logic is now wired:
- Loads challenges via hydrogen.challenges
- Applies miner strategy
- Runs forward (stub → real PhysicsNeMo later)
- Evaluates hard physics gates
- Computes log-improvement score
- Returns structured ValidationResult for consensus

Still a skeleton for full Bittensor axon/dendrite, but the scientific core is functional.
"""

import argparse
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import bittensor as bt
import torch

# Core Hydrogen modules (now integrated)
from hydrogen.challenges.poisson_2d import load_challenge
from hydrogen.physics.gates import evaluate_all_gates, compute_relative_l2_error


@dataclass
class ValidationResult:
    """Structured result returned to consensus / Landscape."""
    challenge_id: str
    score: float
    improvement: float
    hard_pass: bool
    gate_details: Dict[str, Any]
    submission_error: float
    baseline_error: float
    metadata: Dict[str, Any]


def dummy_physics_neural_operator_forward(
    challenge, strategy: dict
) -> Dict[str, torch.Tensor]:
    """Placeholder for real PhysicsNeMo / PINO / FNO training + inference.

    TODO: Replace with actual model loading + training loop using
    strategy['pino']['loss_vector'], curriculum, UQ config, etc.
    """
    stress = challenge.stress_data
    u_true = stress["u_true"][0]

    noise_level = strategy.get("noise_level", 0.015)
    u_pred = u_true + noise_level * torch.randn_like(u_true)

    # Physics fields needed by gates
    div_u = 0.0008 * torch.randn_like(u_true)  # very small for Poisson
    energy_traj = torch.linspace(1.0, 0.975, 60) + 0.0005 * torch.randn(60)

    return {
        "u_pred": u_pred,
        "u_bc": u_true * 0.0,   # Dirichlet BC placeholder
        "div_u": div_u,
        "u_norm": u_true,
        "energy_trajectory": energy_traj,
        "uq_coverage": 0.905,
        "dE_dt": torch.tensor([-0.00025]),
    }


def validate_submission(
    challenge_id: str,
    strategy: dict,
    pde_type: str = "poisson",
) -> ValidationResult:
    """Main validation entrypoint (used by forward() and local scripts).

    This is the function that will be called inside the Bittensor validator forward.
    """
    bt.logging.info(f"Validating submission for {challenge_id}")

    challenge = load_challenge(challenge_id)
    baseline_error = challenge.baseline_error

    # Run the (stub) model
    results = dummy_physics_neural_operator_forward(challenge, strategy)

    # Hard physics gates
    hard_pass, gate_details = evaluate_all_gates(results, pde_type=pde_type)

    if not hard_pass:
        return ValidationResult(
            challenge_id=challenge_id,
            score=0.0,
            improvement=0.0,
            hard_pass=False,
            gate_details=gate_details,
            submission_error=1.0,
            baseline_error=baseline_error,
            metadata={"reason": "hard_physics_gate_failure"},
        )

    # Compute improvement
    u_pred = results["u_pred"]
    u_true = challenge.stress_data["u_true"][0]
    submission_error = compute_relative_l2_error(u_pred, u_true)
    improvement = torch.log(torch.tensor(baseline_error)) - torch.log(torch.tensor(submission_error))
    improvement = float(improvement)

    # Final score (can add soft penalties + UQ bonus later)
    score = max(0.0, improvement)

    return ValidationResult(
        challenge_id=challenge_id,
        score=score,
        improvement=improvement,
        hard_pass=True,
        gate_details=gate_details,
        submission_error=submission_error,
        baseline_error=baseline_error,
        metadata={
            "strategy": strategy,
            "symbolic_metadata_used": challenge.symbolic_metadata.get("suggested_loss_weights"),
        },
    )


def forward(self, synapse: Any) -> Any:  # placeholder for real Bittensor Synapse
    """Bittensor forward hook (to be wired to actual Synapse when axon is added)."""
    # Example: synapse contains challenge_id and strategy JSON from miner
    challenge_id = getattr(synapse, "challenge_id", "poisson_2d_v1")
    strategy = getattr(synapse, "strategy", {})

    result = validate_submission(challenge_id, strategy)

    # In real implementation: attach result to synapse for response
    bt.logging.info(f"Validation complete. Score={result.score:.4f}, HardPass={result.hard_pass}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Hydrogen Validator (now with working core)")
    parser.add_argument("--netuid", type=int, default=107)
    parser.add_argument("--wallet.name", type=str, default="validator")
    parser.add_argument("--wallet.hotkey", type=str, default="default")
    parser.add_argument("--challenge", default="poisson_2d_v1")
    parser.add_argument("--noise", type=float, default=0.012)
    args = parser.parse_args()

    bt.logging.info("Hydrogen Validator starting (integrated core)...")

    # Demo standalone run (no full Bittensor network needed yet)
    strategy = {
        "backbone": "PINO",
        "pino": {"loss_vector": {"pde_residual": 1.0, "boundary": 0.8}},
        "noise_level": args.noise,
    }

    result = validate_submission(args.challenge, strategy)
    print("\n=== Validator Result ===")
    print(f"Score: {result.score:.4f}")
    print(f"Improvement: {result.improvement:+.4f}")
    print(f"Hard Pass: {result.hard_pass}")
    print(f"Submission Error: {result.submission_error:.4f}")
    print("Gate Details:")
    for k, v in result.gate_details.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
