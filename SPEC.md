# SPEC.md — Hydrogen PDE Subnet Technical Specification

**Version:** 3.4 (Updated July 2026)
**Status:** Active Development

---

## 1. System Overview

### 1.1 Core Loop

```
Challenge Release → Strategy Submission → Validator Training + Hidden Stress Testing → Physics-Gated Scoring → ChallengeWinnerTracker → Weights (Yuma) → Landscape Learning
```

### 1.2 Design Philosophy
Physics fidelity first, adversarial robustness via hidden stress + hard gates, decentralized strategy discovery, and information asymmetry.

### 1.3 Current Economics
Standard Yuma Consensus + `ChallengeWinnerTracker` (winner-heavy + exponential decay + dust). Hybrid bounty/stipend model is planned but not active.

---

## 2. Scoring, Physics Gates & Stress Testing

### 2.1 Multi-Objective Scoring (45/30/25)
Physics Fidelity, Robustness, Accuracy → combined score. Only new combined bests on a challenge receive strong weight.

### 2.2 Physics Gates
Hard gates (mass conservation, energy dissipation, boundary satisfaction, rollout stability, UQ calibration) and soft gates with multiplicative penalties. Phase-field specific gates also defined.

### 2.3 Stress Test Design (Transparency & Auditability)

Hydrogen uses a hidden, physics-grounded stress testing system to evaluate robustness under conditions that miners and agents cannot access during development.

**Core Principles**
- **Hidden**: Stress conditions are not derivable from public challenge data.
- **Deterministic & Reproducible**: Given `challenge_id` + validator hotkey, the exact same stress set can be regenerated.
- **Auditable**: Other validators can verify and reproduce stress sets for dispute resolution.
- **Physics-Grounded**: Every stress variant has a clear physical justification.
- **Access-Controlled**: Raw stress data is validator-private until after scoring.

**Architecture**
- **Tier 1 (Procedural)**: Deterministic parametric variations tailored to physics class (Re, geometry, boundary conditions, coefficients, coupling strength, etc.).
- **Tier 2 (Data-Driven)**: Relevant slices from The Well dataset with physics-preserving augmentations.
- **Tier 3 (Future)**: Adversarial / uncertainty-guided / Pareto-front stress generation.

**Seeding Strategy**
Hierarchical deterministic seeding derived from `challenge_id` + validator hotkey ensures full reproducibility while keeping stress hidden.

**Audit Process**
- Any validator can regenerate the exact `StressTestSet` from public inputs + validator identity.
- All stress variants include provenance metadata and physical justification.
- Dispute resolution is supported via independent regeneration and re-evaluation.

See `docs/STRESS_TEST_DESIGN.md` for the full detailed specification.

### 2.4 ChallengeWinnerTracker
Per-challenge best score + leader tracking with exponential decay. Produces winner-heavy + participation dust weights.

---

## 3. Symbolic Layer (Planned)

**ModelingToolkit.jl** for symbolic PDE representation and auto loss weights.

**DataDrivenDiffEq.jl + PySR** for the Symbolic Regression track (discover governing equations from trajectories, validated on hidden stress data).

Symbolic metadata will be preserved through specialist distillation (Symbolic Gauntlet).

---

## 4. Phased Roadmap

### Phase 0 (Current — Completed)
Core infrastructure: `ChallengeWinnerTracker`, `StrategyStore`, multi-objective physics-gated scorer, validator, MCP server, determinism.

### Phase 1: Customization & Data Ingestion
- Same 7 core PDE challenges
- Miners submit LoRA adapters + custom datasets
- **Abaqus ODB / .fil Ingestion Pipeline**
- Expanded symbolic regression track using **PySR** + DataDrivenDiffEq

### Phase 2: Multi-Physics Composition

**Coupling Framework: preCICE**

preCICE is the primary coupling library for Phase 2 multi-physics challenges. Specialists act as black-box participants (or via a Hydrogen adapter layer). The validator orchestrates coupled simulations and evaluates results against physics gates.

**Phase 2A** — Verified FSI (Turek/Hron) and CHT benchmarks using preCICE + established solvers.
**Phase 2B** — Thermo-Elasticity with ~48 Tier-1 references.
**Phase 2C** — Variant expansion on FSI/CHT/Thermo-elasticity.

### Phase 3: 3D Multi-Physics
3D FSI, Thermo-Elasticity, and CHT with turbulence bridge, 3D-specific gates, and curriculum from 2D → 3D specialists.

---

## 5. Validator & Scoring Details

(Full physics gates tables and multi-objective formula are defined in earlier sections.)

---

## 6. Future Domains

See `docs/FUTURE_DOMAINS.md` for the full analysis of additional domains.

---

## 7. Current Limitations

- Full stress test pipeline (including Well integration and access control) and preCICE-based multi-physics composition are planned but not yet implemented.
- Hybrid emissions model is defined but not active.
- Landscape Agent and Symbolic Gauntlet are future work.

---

*This specification reflects both current implementation and the planned phased roadmap.*
