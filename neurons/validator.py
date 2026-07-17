"""Hydrogen Validator (Bittensor neuron - Phase 0 MVP).

Now uses real PhysicsNeMo training when available.
"""

import argparse
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import bittensor as bt
import torch

# Core Hydrogen modules
from hydrogen.challenges.poisson_2d import load_challenge
from hydrogen.physics.gates import evaluate_all_gates, compute_relative_l2_error

from hydrogen.training.physicsnemo_trainer import train_physics_neural_operator


@dataclass
class ValidationResult:
    challenge_id: str
    score: float
    improvement: float
    hard_pass: bool
    gate_details: Dict[str, Any]
    submission_error: float
    baseline_error: float
    metadata: Dict[str, Any]


def validate_submission(
    challenge_id: str,
    strategy: dict,
    pde_type: str = "poisson",
    use_real_training: bool = True,
) -> ValidationResult:
    """Main validation entrypoint with real PhysicsNeMo training."""
    bt.logging.info(f"Validating submission for {challenge_id}")

    challenge = load_challenge(challenge_id)
    baseline_error = challenge.baseline_error

    # === Real training path (PhysicsNeMo) ===
    if use_real_training:
        results = train_physics_neural_operator(challenge, strategy, epochs=6)
    else:
        # Fallback dummy (for quick testing without PhysicsNeMo)
        from hydrogen.training.physicsnemo_trainer import _dummy_fallback
        results = _dummy_fallback(challenge, strategy)

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
    improvement = float(torch.log(torch.tensor(baseline_error)) - torch.log(torch.tensor(submission_error)))

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
            "used_real_training": use_real_training,
            "symbolic_weights": challenge.symbolic_metadata.get("suggested_loss_weights"),
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Hydrogen Validator with real PhysicsNeMo training")
    parser.add_argument("--challenge", default="poisson_2d_v1")
    parser.add_argument("--noise", type=float, default=0.012)
    parser.add_argument("--real", action="store_true", help="Force real PhysicsNeMo training (requires physicsnemo installed)")
    args = parser.parse_args()

    strategy = {
        "backbone": "PINO",
        "pino": {
            "loss_vector": {"pde_residual": 1.2, "boundary": 0.9}
        },
        "modes": 12,
        "width": 24,
        "noise_level": args.noise,
    }

    result = validate_submission(
        args.challenge,
        strategy,
        use_real_training=args.real
    )

    print("\n=== Validator Result (PhysicsNeMo path) ===")
    print(f"Score: {result.score:.4f}")
    print(f"Improvement: {result.improvement:+.4f}")
    print(f"Hard Pass: {result.hard_pass}")
    print(f"Used real training: {result.metadata.get('used_real_training')}")
    print("Gate Details:")
    for k, v in result.gate_details.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
