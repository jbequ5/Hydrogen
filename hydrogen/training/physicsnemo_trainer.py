"""Training entrypoint updated to respect multi-backbone strategies."""

from typing import Dict, Any

import torch

from hydrogen.training.trainer import get_model, train_model


def train_physics_neural_operator(
    challenge,
    strategy: dict,
    epochs: int = 50,
) -> Dict[str, Any]:
    """
    Main training function that now supports multiple backbones.
    """
    backbone = strategy.get("backbone", challenge.get_backbone() if hasattr(challenge, "get_backbone") else "physicsnemo_fno")

    # Get model from registry
    model = get_model(
        backbone=backbone,
        in_channels=3,
        out_channels=1,
    )

    # Simple dummy data loader for now (replace with real PDEBench loader)
    # In production this would use challenge.stress_data or PDEBench
    x = torch.randn(8, 3, 64, 64)
    y = torch.randn(8, 1, 64, 64)

    train_loader = [(x, y)] * 20

    result = train_model(
        model=model,
        train_loader=train_loader,
        epochs=epochs,
        lr=strategy.get("learning_rate", 0.001),
    )

    return {
        "model": result["model"],
        "backbone": backbone,
        "history": result.get("history", {}),
        "u_pred": torch.randn(1, 1, 64, 64),  # Placeholder
    }
