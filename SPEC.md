# SPEC.md — Hydrogen Technical Specification (Current State)

**Last Updated:** July 18, 2026

This document describes the **actual implemented design** of Hydrogen as of the current codebase, rather than the original ambitious vision.

---

## Overview

Hydrogen is a Bittensor subnet for the decentralized discovery of better **Physics-Informed Neural Operators** for solving Partial Differential Equations (PDEs). 

Miners submit training strategies. Validators run team-defined evaluation plans that include hidden stress testing with hard physics constraints. A causal reasoning layer (the Landscape Agent) identifies what actually improves performance and distills successful strategies into reusable specialists.

The system is designed so that **only verifiable, physics-correct generalization** reliably earns rewards.

---

## Current Architecture

```
Miners
  ↓ submit strategy JSON (backbone, loss weights, curriculum, UQ config)
Validators
  ↓ execute get_evaluation_plan() → train on benchmark + hidden stress test + physics gates
Landscape Agent
  ↓ causal inference (Double ML + CATE) + novelty scoring
  ↓ propose distillation → distill → register in Specialist Bank
  ↓ auto-generate improved published priors
Specialist Bank
  ↓ versioned, validated specialists with metadata
```

---

## Key Implemented Components

| Component                    | Status      | Description |
|--------------------------------|-------------|-------------|
| **Backbone Registry**          | Complete    | Supports `physicsnemo_fno`, `fno`, `deeponet`, `uno` |
| **Unified Trainer**            | Complete    | `get_model()` + training loop with validation support |
| **Benchmark Loader**           | Complete    | PDEBench + synthetic fallback + NeuralOperator extensibility |
| **Evaluation Plans**           | Complete    | `get_evaluation_plan(challenge_id, backbone)` — team-controlled |
| **Adaptive Stress Difficulty** | Complete    | EMA + noise + conservative floor (anti-sandbagging) |
| **Real Ground Truth**          | Complete    | `u_true` loaded from benchmark test split |
| **Landscape Agent**            | Advanced    | Double ML + CATE, novelty-aware distillation proposals, auto prior generation |
| **Specialist Bank**            | Functional  | Register, query, and manage distilled specialists |
| **Emission Mechanics**         | Complete    | 75% Breakthrough Bounties + 25% Decaying Top-2 Stipend |

---

## How Scoring Works

### Data Flow

For any `(challenge_id, backbone)`:

1. **Train** on the benchmark training split.
2. **Stress Test** using procedurally generated hidden conditions (with adaptive difficulty).
3. **Evaluate** using real ground truth (`u_true`) from the benchmark test split.
4. Apply **hard physics gates** (divergence, energy stability, boundary conditions, rollout stability).
5. If any hard gate fails → score = 0.
6. Otherwise, compute **log-space improvement** over the current baseline.

### Score Calculation

```python
improvement = log(E_baseline) - log(E_submission)
score = improvement   # (plus soft factors in future)
```

The **baseline** is the best error achieved so far on hidden stress conditions.

---

## Strategy JSON (What Miners Submit)

Miners submit rich strategy JSONs containing:
- `backbone`
- `loss_vector`
- Curriculum settings
- UQ configuration
- Optimizer / learning rate / epochs

**Miners do NOT control data splits or stress conditions.** These are defined exclusively by the team in `get_evaluation_plan()`.

---

## Evaluation Plans (Team-Controlled)

The core routing logic lives in `hydrogen/evaluation/plan.py`:

```python
def get_evaluation_plan(challenge_id, backbone, hotkey):
    return {
        "train_loader": get_benchmark_loader(challenge_id, split="train"),
        "stress_conditions": generate_stress_conditions(challenge_id, difficulty=adaptive),
        "benchmark_loader": get_benchmark_loader(challenge_id, split="test"),
        "adaptive_difficulty": get_adaptive_difficulty(hotkey),
    }
```

This function is **team-controlled**. Validators simply execute whatever plan is defined here.

---

## Landscape Agent

The Landscape Agent performs:
- Causal inference using Double Machine Learning + Heterogeneous Treatment Effects (CATE)
- Novelty scoring when ranking distillation candidates
- Only proposes distillation when causal effect is positive
- Automatically generates improved (noisy) published priors after successful distillation

It maintains a growing causal knowledge base and helps the system compound knowledge over time.

---

## Emission Mechanics (75/25 Model)

- **75%** → Breakthrough Bounties (paid on new stress test records, with cooldown + accumulation)
- **25%** → Decaying Top-2 Stipend (only current leaders; requires minimum improvement; decays without progress)

Strong anti-gaming features are built in.

---

## Anti-Gaming Measures

- Hidden procedural stress tests (miners never see the exact conditions)
- Hard physics gates (binary pass/fail)
- Adaptive stress difficulty with anti-sandbagging (EMA + noise + floor)
- Real ground truth from benchmark test splits
- No miner control over data splits or evaluation conditions
- Validator is the executor; the team defines the rules

---

## Current Limitations (Honest)

- Single validator logic (no median consensus yet)
- No Julia Symbolic Layer / ModelingToolkit integration yet
- Distillation pipeline is basic (not yet multi-teacher + full ONNX workflow)
- No full on-chain pallet mechanics yet

---

## Philosophy

Hydrogen is built on the principle that **the things that pay should be the things that matter scientifically**:
- Physics correctness under unseen conditions
- Verifiable generalization
- Causal understanding of what actually improves performance

The incentive structure is the product.
