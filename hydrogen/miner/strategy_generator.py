"""Strategy generator with multi-backbone support."""

from typing import Dict, Any

from hydrogen.challenges import load_challenge
from hydrogen.backbones import list_backbones


def generate_strategy(challenge_id: str = "poisson_2d_v1", backbone: str = None) -> Dict[str, Any]:
    try:
        challenge = load_challenge(challenge_id)
        symbolic = challenge.symbolic_metadata
        suggested_weights = symbolic.get("suggested_loss_weights", {})

        # Use provided backbone or fall back to challenge default
        chosen_backbone = backbone or challenge.get_backbone()

    except Exception:
        suggested_weights = {"pde_residual": 1.0, "boundary": 0.8}
        chosen_backbone = backbone or "physicsnemo_fno"

    return {
        "backbone": chosen_backbone,
        "resolution": list(getattr(challenge, "resolution", [128, 128])),
        "pino": {
            "loss_vector": suggested_weights,
            "physics_loss_type": "pde_residual",
            "boundary_handling": "ghost_cells",
        },
        "optimizer": "AdamW",
        "learning_rate": 0.001,
        "epochs": 80,
        "curriculum_learning": {
            "enabled": True,
            "start_resolution": [64, 64],
            "end_resolution": list(getattr(challenge, "resolution", [128, 128])),
            "ramp_epochs": 30,
        },
        "uq_config": {
            "method": "deep_ensemble",
            "num_members": 3,
            "calibration_target": 0.90,
        },
        "auto_loss_weights": True,
    }


def list_available_backbones():
    return list_backbones()
