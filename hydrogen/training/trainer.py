"""Highly modular trainer supporting many strategy-controlled options."""

from typing import Dict, Any, Optional

import torch
import torch.nn as nn

from hydrogen.backbones import get_backbone


def get_model(
    backbone: str = "physicsnemo_fno",
    in_channels: int = 3,
    out_channels: int = 1,
    **kwargs,
) -> nn.Module:
    BackboneClass = get_backbone(backbone)
    return BackboneClass(in_channels=in_channels, out_channels=out_channels, **kwargs)


def get_optimizer(model: nn.Module, strategy: dict):
    opt_name = strategy.get("optimizer", "AdamW").lower()
    lr = strategy.get("learning_rate", 0.001)
    weight_decay = strategy.get("weight_decay", 1e-4)

    if opt_name == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif opt_name == "adam":
        return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif opt_name == "sgd":
        momentum = strategy.get("momentum", 0.9)
        return torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    else:
        return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)


def get_scheduler(optimizer, strategy: dict, epochs: int):
    scheduler_name = strategy.get("scheduler", "CosineAnnealingLR").lower()

    if scheduler_name == "cosineannealinglr":
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    elif scheduler_name == "steplr":
        step_size = strategy.get("step_size", max(1, epochs // 4))
        gamma = strategy.get("gamma", 0.5)
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif scheduler_name == "reducelronplateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=10)
    else:
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)


def train_model(
    model: nn.Module,
    train_loader,
    val_loader: Optional[Any] = None,
    strategy: dict = None,
    epochs: int = 50,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    physics_loss_fn: Optional[callable] = None,
) -> Dict[str, Any]:
    if strategy is None:
        strategy = {}

    model = model.to(device)
    optimizer = get_optimizer(model, strategy)
    scheduler = get_scheduler(optimizer, strategy, epochs)

    # Gradient clipping
    grad_clip_norm = strategy.get("grad_clip_norm", None)

    # Gradient accumulation
    accumulation_steps = strategy.get("accumulation_steps", 1)

    # Mixed precision
    use_amp = strategy.get("use_amp", False) and device.startswith("cuda")
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    # Early stopping (basic)
    early_stop_patience = strategy.get("early_stop_patience", None)
    best_val_loss = float("inf")
    epochs_no_improve = 0

    history = {"train_loss": [], "val_loss": []}

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        optimizer.zero_grad()

        for i, batch in enumerate(train_loader):
            x, y = batch[0].to(device), batch[1].to(device)

            if use_amp:
                with torch.cuda.amp.autocast():
                    pred = model(x)
                    loss = torch.nn.functional.mse_loss(pred, y)
                    if physics_loss_fn is not None:
                        loss = loss + physics_loss_fn(pred, x)
                scaler.scale(loss).backward()
            else:
                pred = model(x)
                loss = torch.nn.functional.mse_loss(pred, y)
                if physics_loss_fn is not None:
                    loss = loss + physics_loss_fn(pred, x)
                loss.backward()

            # Gradient accumulation
            if (i + 1) % accumulation_steps == 0:
                if grad_clip_norm:
                    if use_amp:
                        scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)

                if use_amp:
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()

                optimizer.zero_grad()

            total_loss += loss.item()

        avg_train = total_loss / len(train_loader)
        history["train_loss"].append(avg_train)

        # Validation
        current_val_loss = None
        if val_loader is not None:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch in val_loader:
                    x, y = batch[0].to(device), batch[1].to(device)
                    pred = model(x)
                    val_loss += torch.nn.functional.mse_loss(pred, y).item()
            current_val_loss = val_loss / len(val_loader)
            history["val_loss"].append(current_val_loss)

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Train: {avg_train:.6f} | Val: {current_val_loss:.6f}")
        else:
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train:.6f}")

        # Scheduler step
        if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau) and current_val_loss is not None:
            scheduler.step(current_val_loss)
        else:
            scheduler.step()

        # Early stopping
        if early_stop_patience and current_val_loss is not None:
            if current_val_loss < best_val_loss - 1e-6:
                best_val_loss = current_val_loss
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1

            if epochs_no_improve >= early_stop_patience:
                print(f"Early stopping triggered at epoch {epoch+1}")
                break

    return {"model": model, "history": history}
