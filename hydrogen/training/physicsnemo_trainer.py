"""Training function updated with real benchmark loading support."""

from typing import Dict, Any

import torch

from hydrogen.training.trainer import get_model, train_model
from hydrogen.data.benchmark_loader import get_benchmark_loader


def train_physics_neural_operator(
    challenge,
    strategy: dict,
    epochs: int = 50,
) -> Dict[str, Any]:
    backbone = strategy.get("backbone", challenge.get_backbone() if hasattr(challenge, "get_backbone") else "physicsnemo_fno")

    model = get_model(backbone=backbone, in_channels=3, out_channels=1)

    # Try to load real benchmark data
    challenge_id = getattr(challenge, "challenge_id", "unknown")
    train_loader = get_benchmark_loader(challenge_id, batch_size=8, split="train")

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
        "u_pred": torch.randn(1, 1, 64, 64),  # Placeholder for now
    }
