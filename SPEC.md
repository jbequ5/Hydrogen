# SPEC.md — Hydrogen Technical Specification (Current Implementation)

**Status:** Accurate reflection of the codebase as of July 18, 2026.

This document describes what actually exists in code, not the original ambitious vision.

---

## 1. Overview

Hydrogen is a Bittensor subnet focused on the decentralized discovery of better **Physics-Informed Neural Operators** for solving PDEs.

Core principles:
- Miners submit training strategies (not weights).
- Validators execute team-defined evaluation plans.
- Evaluation includes hidden stress testing with hard physics constraints.
- A causal reasoning layer (Landscape Agent) guides what gets distilled.
- Only verifiable, physics-correct generalization earns meaningful rewards.

---

## 2. Current Architecture

```
Miners
  ↓ submit rich strategy JSON
Validators
  ↓ get_evaluation_plan(challenge_id, backbone)
  ↓ Train on benchmark train split
  ↓ Run hidden procedural stress tests (adaptive difficulty)
  ↓ Evaluate with real u_true from benchmark test split
  ↓ Apply hard physics gates
Landscape Agent
  ↓ Ingests validation results
  ↓ Runs Double ML + CATE causal inference
  ↓ Novelty + causal scoring for distillation candidates
  ↓ Distills → Specialist Bank
  ↓ Auto-generates improved published priors
Specialist Bank
  ↓ Stores versioned, validated specialists
```

---

## 3. Challenges (Current)

We currently support the following PDE challenges:

| Challenge ID          | PDE Type          | Dimension | Notes                          |
|-----------------------|-------------------|-----------|--------------------------------|
| `poisson_2d_v1`       | Poisson           | 2D        | Elliptic, constant coefficient |
| `darcy_2d_v1`         | Darcy Flow        | 2D        | Variable permeability          |
| `burgers_v1`          | Burgers           | 1D        | Nonlinear advection + shocks   |
| `heat_v1`             | Heat Equation     | 2D        | Diffusion                      |
| `elasticity_2d_v1`    | Linear Elasticity | 2D        | Structural mechanics           |
| `ns_2d_laminar_v1`    | Navier-Stokes     | 2D        | Incompressible laminar flow    |

Each challenge has associated benchmark data (via PDEBench where available) and procedurally generated hidden stress conditions.

---

## 4. Evaluation Plans (`get_evaluation_plan`)

The core routing logic lives in `hydrogen/evaluation/plan.py`.

```python
def get_evaluation_plan(challenge_id, backbone, hotkey):
    return {
        "train_loader": get_benchmark_loader(challenge_id, split="train"),
        "stress_conditions": generate_stress_conditions(challenge_id, difficulty=adaptive_difficulty),
        "benchmark_loader": get_benchmark_loader(challenge_id, split="test"),
        "adaptive_difficulty": get_adaptive_difficulty(hotkey),
    }
```

**Key properties:**
- Fully controlled by the team (not miners).
- Separates train / stress / benchmark data streams.
- Adaptive difficulty includes anti-sandbagging (EMA + noise + floor).

---

## 5. Stress Testing

### 5.1 Stress Condition Generation
Located in `hydrogen/physics/stress.py`:

- Procedurally generated per challenge using deterministic seeding.
- Includes parameter perturbation, noise, resolution scaling, Reynolds/viscosity multipliers, etc.
- Difficulty is adaptive based on recent miner performance.

### 5.2 Hard Physics Gates (Current)

| Gate                        | Applies To          | Condition                          | Consequence      |
|-----------------------------|---------------------|------------------------------------|------------------|
| Divergence-free             | Navier-Stokes       | `max(|divergence|) > tolerance`    | Hard fail        |
| Long-term energy stability  | Most fluid PDEs     | Large energy drift over rollout    | Hard fail        |
| Negative energy             | Burgers             | Energy < 0                         | Hard fail        |
| Boundary satisfaction       | All                 | Large boundary error               | Hard fail        |
| Rollout stability           | All                 | Large drift in energy/fields       | Hard fail        |

If any hard gate fails → score = 0.

### 5.3 Ground Truth (`u_true`)

Real ground truth is loaded from the benchmark **test split** using `get_ground_truth_batch()`. This replaced earlier placeholder zeros.

---

## 6. Scoring

Current scoring logic (in `neurons/validator.py`):

1. Train model using miner strategy.
2. Run hidden stress test with real `u_true`.
3. If hard gates pass:
   - Compute improvement over current baseline (log-space).
   - Apply adaptive difficulty weighting.
4. Final score is primarily driven by stress test performance + physics correctness.

**Note:** We are currently using a simplified scoring version focused on stress performance. More sophisticated public holdout + stress combination can be added later.

---

## 7. Miner Strategy JSON

Miners submit strategies containing:

```json
{
  "backbone": "fno" or "physicsnemo_fno" or "deeponet" or "uno",
  "loss_vector": { ... },
  "curriculum_learning": { ... },
  "uq_config": { ... },
  "optimizer": "AdamW",
  "learning_rate": 0.0008,
  "epochs": 100
}
```

**Important:** `data_split` is **not** part of the miner strategy. Data routing is controlled exclusively by `get_evaluation_plan()`.

---

## 8. Landscape Agent (Current State)

Located in `hydrogen/landscape/agent.py`:

Current capabilities:
- Ingests validation results (scores, stress metrics, backbone used).
- Runs Double Machine Learning + basic Heterogeneous Treatment Effects (CATE).
- Ranks distillation candidates using combined **causal effect strength + novelty**.
- Only proposes distillation when causal effect is positive.
- After successful distillation, automatically generates improved (noisy) published priors.
- Maintains growing causal knowledge base.

---

## 9. Specialist Bank

Located in `hydrogen/specialist/bank.py`:

- Stores distilled specialists with metadata (version, challenge, backbone, causal_ate, novelty_score, etc.).
- Supports registration, querying by challenge, and retrieving best specialist per challenge.
- Integrated with distillation pipeline.

---

## 10. Emission Mechanics (Current 75/25 Model)

- **75%** → Breakthrough Bounties
  - Paid when a new stress test record is set.
  - Includes cooldown period and bounty accumulation.
- **25%** → Decaying Top-2 Stipend
  - Only current #1 and #2 on each challenge receive this.
  - Requires minimum improvement to remain eligible.
  - Decays with `epochs_without_improvement`.
  - Anti-camping logic included.

---

## 11. Anti-Gaming Measures (Implemented)

- Hidden procedural stress conditions (miners never see exact test cases).
- Hard physics gates (binary failure).
- Adaptive stress difficulty with anti-sandbagging (EMA + noise + floor).
- Real ground truth from benchmark test splits.
- No miner control over data splits or evaluation conditions.
- Validator executes team-defined plans.

---

## 12. Honest Current Gaps

- Single validator logic (no median consensus yet).
- No Julia Symbolic Layer / ModelingToolkit integration yet.
- Distillation is functional but not yet advanced multi-teacher + full ONNX workflow.
- No full on-chain challenge/pallet mechanics yet.
- Scoring is currently stress-focused; public holdout weighting can be strengthened.

---

## 13. Philosophy

Hydrogen is built around one core idea:

> The things that pay should be the things that matter scientifically.

That means hidden stress testing, hard physics constraints, causal understanding of what improves performance, and verifiable generalization — not just fitting public data.
