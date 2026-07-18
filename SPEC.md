# SPEC.md — Hydrogen Technical Specification (Current Implementation)

**Status:** Accurate reflection of the codebase as of July 18, 2026.

---

## 1. Overview

Hydrogen is a Bittensor subnet for decentralized discovery of better Physics-Informed Neural Operators. Miners submit training strategies. Validators run team-defined evaluation plans with hidden stress testing and hard physics gates. A causal reasoning layer (Landscape Agent) identifies what works and distills it into specialists.

---

## 2. Miner Strategy JSON (Rich & Modular)

Miners can control many aspects of training via the strategy. Example:

```json
{
  "backbone": "fno",
  "resolution": [128, 128],

  "pino": {
    "loss_vector": {
      "pde_residual": 1.0,
      "conservation_mass": 1.2,
      "boundary": 0.6
    }
  },

  "optimizer": "AdamW",
  "learning_rate": 0.0008,
  "weight_decay": 1e-4,

  "scheduler": "CosineAnnealingLR",

  "weight_init": "kaiming_normal",

  "grad_clip_norm": 1.0,
  "accumulation_steps": 4,
  "use_amp": true,

  "physics_loss_weight": 0.8,

  "early_stop_patience": 15,

  "batch_size": 8,
  "epochs": 120,

  "curriculum_learning": {
    "enabled": true,
    "start_resolution": [64, 64],
    "end_resolution": [128, 128],
    "ramp_epochs": 40
  },

  "uq_config": {
    "enabled": true,
    "method": "deep_ensemble",
    "num_members": 4
  },

  "model_kwargs": {
    "modes": 32,
    "width": 64
  }
}
```

**Note:** Miners do **not** control data splits or hidden stress conditions. These are defined by the team via `get_evaluation_plan()`.

---

## 3. Evaluation Plans

Defined in `hydrogen/evaluation/plan.py`. The validator uses this to decide exactly what data and conditions to use for each challenge.

---

## 4. Stress Testing & Physics Gates

- Procedurally generated hidden conditions per challenge.
- Adaptive difficulty with anti-sandbagging (EMA + noise + floor).
- Hard gates: divergence, energy stability, boundary conditions, rollout stability, negative energy.
- Real `u_true` loaded from benchmark test split.

---

## 5. Current Modularity (What Miners Can Control)

| Category              | Fields                                      | Impact on Causal Learning |
|-----------------------|---------------------------------------------|---------------------------|
| Backbone              | fno, deeponet, uno, physicsnemo_fno         | High                      |
| Optimizer             | AdamW, Adam, SGD                            | High                      |
| Learning Rate         | Any float                                   | High                      |
| Scheduler             | Cosine, Step, ReduceLROnPlateau             | Medium-High               |
| Weight Initialization | kaiming_*, xavier_*, normal                 | Medium                    |
| Gradient Clipping     | grad_clip_norm                              | Medium                    |
| Mixed Precision       | use_amp                                     | Medium                    |
| Gradient Accumulation | accumulation_steps                          | Low-Medium                |
| Physics Loss Weight   | physics_loss_weight                         | High                      |
| Early Stopping        | early_stop_patience                         | Low                       |
| Curriculum            | start/end resolution, ramp_epochs           | High                      |
| UQ Configuration      | method, num_members, calibration_target     | Medium                    |
| Model-specific        | model_kwargs (modes, width, etc.)           | High                      |

---

## 6. Analysis: Is This the Optimal Customization Path?

**Pros of high modularity:**
- Gives the Landscape Agent rich, high-dimensional data to learn causal effects from.
- Allows genuinely novel training strategies to emerge.
- Lowers barrier for creative researchers (they can experiment with many levers).
- Aligns with the goal of decentralized discovery.

**Cons / Risks:**
- Increased complexity for miners (strategy space is large).
- Higher risk of spurious correlations or gaming (e.g., tuning many knobs to barely pass gates).
- Validator code becomes more complex.
- Some knobs may have weak or noisy causal signals.

**Recommendation:**

This level of modularity is **mostly optimal** for Phase 0/1, with two caveats:

1. **Document recommended ranges** and sensible defaults clearly (e.g., in docs or via `hydrogen-miner baseline`).
2. **Let the Landscape Agent learn** which knobs actually matter. Over time it can propose simpler, high-signal strategies to miners.

We should **not** arbitrarily limit customization early. The causal layer is designed exactly to discover which combinations are valuable.

If complexity becomes a problem later, we can add "strategy templates" or "recommended presets" while still allowing advanced users full control.

---

## 7. Honest Gaps

- Single validator (no median consensus yet)
- No advanced multi-teacher distillation pipeline yet
- No full on-chain mechanics yet
- Symbolic Layer (Julia) not yet integrated

---

## 8. Summary

Hydrogen currently offers a highly modular training interface. Miners can control most meaningful training decisions through the strategy JSON. The Landscape Agent is positioned to learn causally from the effects of these choices. This design maximizes the chance of discovering genuinely better physics-informed training strategies in a decentralized way.
