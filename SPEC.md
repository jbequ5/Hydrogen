# SPEC.md — Hydrogen PDE Subnet Technical Specification

**Version:** 3.1 (Updated July 2026)
**Status:** Active Development

This document describes the technical architecture, scoring system, validator design, and long-term roadmap for Hydrogen, a Bittensor subnet (SN63) focused on decentralized discovery of high-quality Physics-Informed Neural Operator (PINO) strategies for engineering simulation.

---

## 1. System Overview

### 1.1 Core Loop

```
Challenge Release → Miner/Agent Strategy Submission → Validator Training + Hidden Stress Testing → Physics-Gated Multi-Objective Scoring → ChallengeWinnerTracker Update → Weight Submission (Yuma) → Landscape Causal Learning → Improved Priors
```

### 1.2 Design Philosophy

Hydrogen is built on four interlocking principles:

1. **Physics Fidelity First** — Every high-value submission must demonstrably respect conservation laws, boundary conditions, stability, and energy dissipation under hidden stress.
2. **Adversarial Robustness** — Hidden stress tests + hard physics gates make gaming and overfitting significantly harder than public-benchmark-only evaluation.
3. **Decentralized Discovery** — The strategy space for good physics-informed training is enormous. Decentralized adversarial iteration surfaces better solutions than any single lab.
4. **Information Asymmetry** — Miners/agents see challenge descriptions, their own scores, and noisy priors — but not hidden stress conditions or exact internal gate logic. This asymmetry is intentional and core to robustness.

### 1.3 Current Economics (Standard Yuma + Winner-Heavy Tracker)

Hydrogen currently uses standard Bittensor Yuma Consensus emissions via `set_weights()`.

The `ChallengeWinnerTracker` produces **winner-heavy + participation dust** weight distributions:
- Strong preference for current per-challenge leaders (on combined Physics + Robustness + Accuracy score)
- Exponential decay on old performance
- Small "dust" allocation to recent participants

A more ambitious hybrid emissions model (Breakthrough Bounties, Decaying Stipends, per-challenge treasury rollover) is defined in the original v2.4 SPEC and remains a planned future direction, but is **not active** in the current implementation.

---

## 2. Scoring System

### 2.1 Three High-Level Objectives (Default 45/30/25)

| Objective | Weight | Description |
|-----------|--------|-------------|
| **Physics Fidelity** | 45% | Residuals, conservation laws, boundary conditions, energy dissipation, stability |
| **Robustness** | 30% | Performance under hidden stress, long-term rollout stability, generalization |
| **Accuracy** | 25% | Benchmark / hold-out performance |

A **combined final score** is computed. Only submissions that beat the current best combined score on a challenge receive meaningful weight from the `ChallengeWinnerTracker`.

### 2.2 Fine-Grained Metrics

The scorer produces rich per-submission diagnostics (used by the Landscape Agent and for debugging):

- Benchmark MSE / relative L2 error / max error
- Physics residual norm
- Divergence error
- Energy stability / conservation error
- Boundary violation
- Long-term rollout stability
- Parameter sensitivity / noise robustness
- Stress generalization

### 2.3 Physics Gates (Stress Test)

#### Hard Gates (Score = 0 if failed)
| Check | Formula | Threshold | Applies To |
|-------|---------|-----------|------------|
| Mass Conservation | ‖∇·u‖₁ / ‖u‖₁ | < 1e-3 | NS, Darcy, Elasticity |
| Energy Dissipation | dE/dt | ≤ 1e-4 | NS, Heat, Burgers |
| Boundary Satisfaction | ‖u - u_BC‖₂ / ‖u_BC‖₂ | < 1e-3 | All with BCs |
| Rollout Stability | ‖E(t=T) - E(t=0)‖ / E(t=0) | < 0.01 | All transient |
| UQ Calibration | |coverage - target| | < 0.02 | All (UQ mandatory) |

#### Phase-Field Specific Hard Gates (when applicable)
| Check | Threshold | Physics Meaning |
|-------|-----------|-----------------|
| Crack Irreversibility (∂d/∂t) | ≥ 0 | No healing |
| Length Scale ℓ Enforcement | < 0.05 | Phase-field consistency |
| Degradation Function g(d) | < 0.05 | Validity of degradation |

#### Soft Gates (Multiplicative Penalty)
| Check | Penalty Function |
|-------|------------------|
| Symmetry | max(0, 1 - 20 × (ratio - 0.05)) |
| Spectral Fidelity | max(0, 1 - 10 × (error - 0.1)) |
| Conservation Drift | max(0, 1 - 100 × drift) |

### 2.4 ChallengeWinnerTracker

The validator maintains a per-challenge `ChallengeWinnerTracker` with:

- Best combined score per challenge
- Current leader hotkey per challenge
- Exponential decay on old performance (default decay_factor = 0.85)
- Winner-heavy + participation dust weight distribution
- `reset_round()` support for daily/round-based heavy discounting

Only submissions that set a new best **combined score** on a challenge contribute strongly to weights.

---

## 3. Symbolic Layer & Equation Discovery (Core Planned Capability)

Hydrogen places strong emphasis on **symbolic reasoning** alongside neural operators. This is not an add-on — it is a first-class part of the long-term architecture.

### 3.1 Goals of the Symbolic Layer

- Extract and exploit symmetries, conservation laws, and dimensionless groups from challenges
- Enable automatic, physics-aware loss weighting
- Support symbolic regression / equation discovery as a distinct competition track
- Preserve symbolic metadata through specialist distillation
- Provide richer features to the Landscape Agent for causal learning

### 3.2 Key Tools

| Tool | Role | Status |
|------|------|--------|
| **ModelingToolkit.jl** | Symbolic PDE representation, conservation laws, symmetries, acausal composition, auto loss weight generation | Planned (Phase 1+) |
| **DataDrivenDiffEq.jl + PySR** | Symbolic regression / equation discovery track. Discover governing PDEs from trajectory data using sparse regression over basis functions. | Planned (Phase 1–2) |
| **Symbolic Metadata Pipeline** | Per-challenge extraction of symmetries, conservation laws, boundary types, coupling terms, and validity domain. Used for auto loss weights and specialist grounding. | Planned |

### 3.3 Symbolic Regression Track (PySR-powered)

Miners/agents can submit discovered PDE strings + basis functions. The validator will:

1. Verify the discovered equation against hidden stress data
2. Compare predictive accuracy and physical consistency against neural baselines
3. Award a **Symbolic Bonus** (planned) when the discovered equation improves baseline by >5% while remaining parsimonious

This track runs in parallel with neural operator submissions and feeds into the Landscape Agent and Specialist Bank.

### 3.4 Symbolic Gauntlet (Future Specialist Promotion)

When distilling specialists, the system will verify that symbolic metadata is preserved:
- Governing PDE / symmetries / conservation laws match the teacher ensemble
- Validity domain is consistent
- Generated CUDA kernels (via ModelingToolkit codegen) are valid and match numerical behavior

---

## 4. Validator Architecture

### 4.1 Components

- `HydrogenScorer` — Multi-objective evaluation (Physics / Robustness / Accuracy + fine-grained metrics)
- `ChallengeWinnerTracker` — Per-challenge leader tracking with exponential decay
- `StrategyStore` — Abstraction for retrieving miner strategies (currently local file backed)
- Backbone images (pinned, pre-built) for deterministic training

### 4.2 Validation Pipeline (High-Level)

1. Retrieve strategy via `StrategyStore`
2. Train backbone on challenge training split (deterministic seed derived from challenge_id + validator hotkey)
3. Evaluate on public holdout
4. Run hidden stress test + physics gates
5. Compute combined score
6. Update `ChallengeWinnerTracker`
7. (Future) Feed rich per-evaluation data + symbolic features to Landscape Agent

### 4.3 Determinism

Training and stress testing are made deterministic via:
- Fixed random seeds derived from challenge_id + validator hotkey
- Pinned backbone images
- Controlled data loading and augmentation

---

## 5. Miner / Agent Interface

### 5.1 Strategy JSON Schema (Current Phase 0-1)

```json
{
  "backbone": "physicsnemo_fno" | "pino" | "deeponet" | ...,
  "challenge_id": "string",
  "epochs": 200,
  "physics_loss_weight": 1.5,
  "boundary_handling": "ghost_cells",
  "curriculum_learning": { ... },
  "uq_config": { ... },
  "custom_data": { ... },
  "backend": "pytorch" | "jax" | "sciml",
  "symbolic_regression": { ... }   // Future track
}
```

### 5.2 Submission Rules (Current)
- One active submission per miner per challenge (last submission counts)
- Format: JSON
- Fee: 0.1 TAO (burned on pre-check failure)

---

## 6. Challenge Specification (Current Focus)

### 6.1 Phase 0 Challenges (7 Core PDEs)

| ID | Problem | Dimension | Key Physics |
|----|---------|-----------|-------------|
| 1 | Poisson | 2D / 3D | Elliptic |
| 2 | Darcy | 2D / 3D | Elliptic, variable coeff |
| 3 | Burgers | 2D | Nonlinear advection/shocks |
| 4 | Navier-Stokes | 2D / 3D (laminar) | Incompressible flow |
| 5 | Heat | 2D | Transient conduction |
| 6 | Elasticity | 2D | Vector mechanics |
| 7 | Thermo-elasticity | 2D | Multi-physics coupling |

Each challenge includes:
- Public training split
- Public holdout
- Hidden stress test data (procedural + Well slices, seeded)
- Symbolic metadata (future)

---

## 7. Future Domains & Expansion Roadmap

See the dedicated document `docs/FUTURE_DOMAINS.md` for a full analysis of high-potential future domains, including:

**Tier 1 (Near-to-Medium Term)**
- Electromagnetics
- Photonics & Optics (including quantum photonics)
- Acoustics & Wave Propagation
- Phase-Field Modeling & Materials Damage/Fracture

**Tier 2 (Strategic)**
- Plasmas & Magnetohydrodynamics (Fusion-relevant)
- Quantum-informed & Hybrid Modeling
- Verified Multi-Physics Composition

**Tier 3 (Longer-Term / Scientific)**
- Gravity (Newtonian + General Relativity)
- Climate & Earth System Modeling
- Nuclear / Radiation Transport
- Biological & Biomechanical Systems

---

## 8. SciML Ecosystem Integration (Planned)

Hydrogen is designed to integrate first-class with the SciML ecosystem:

- **ModelingToolkit.jl** — Symbolic PDE representation, conservation laws, symmetries, acausal composition, auto loss weight generation
- **NeuralOperators.jl / jNO** — Reference neural operator implementations (PyTorch + JAX)
- **DataDrivenDiffEq.jl + PySR** — Symbolic regression / equation discovery track
- **SciMLSensitivity.jl** — High-quality adjoints for physics-informed training
- **PhysicsNeMo + NeuralOperator** — Primary production neural operator stack

These tools will be used for symbolic metadata generation, specialist distillation with symbolic preservation, and advanced hybrid strategies.

---

## 9. Landscape Agent & Causal Learning (Future)

Once rich per-evaluation data pipelines are mature, the Landscape Agent will:

- Ingest StrategyFragments (config, improvement, stress results, physics metrics, symbolic features)
- Enrich with symbolic features extracted via ModelingToolkit / PySR
- Run Double Machine Learning (DML) for heterogeneous treatment effects
- Propose baseline updates and specialist distillation candidates
- Maintain causal lineage for specialist promotion

This component is **not yet active** in the current implementation.

---

## 10. Information Asymmetry & Anti-Gaming

Miners and agents have access to:
- Challenge descriptions
- Their own scores and fine-grained metrics
- Noisy or aggregated priors / leader information

They do **not** have direct access to:
- Hidden stress test conditions and data splits
- Exact physics gate implementations and thresholds
- Full internal scoring logic and `ChallengeWinnerTracker` state
- Raw Landscape Agent data and learned models

This asymmetry is intentional and is one of Hydrogen’s core robustness mechanisms.

---

## 11. Current Limitations & Open Work

- Strategy retrieval is currently local-file based (platform-backed store planned)
- Hybrid emissions model (bounties + stipends + treasury) is defined but not implemented
- Landscape Agent and specialist distillation pipeline are future work
- Multi-validator consistency and canonical ranking not yet stress-tested
- Symbolic layer (ModelingToolkit integration, PySR track, auto loss weights, Symbolic Gauntlet) is planned but not yet active

---

## 12. Documentation & Related Files

- `README.md` — High-level project overview and vision
- `docs/FUTURE_DOMAINS.md` — Detailed future domain analysis (How, Why, Market)
- `docs/VALIDATOR_GUIDE.md` — How to run the validator
- `docs/EMISSIONS.md` — Current emissions model
- `docs/AGENT_USAGE.md` — MCP / Agent interaction guide

---

*This specification is a living document and will be updated as the implementation and roadmap evolve.*
