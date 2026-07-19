# SPEC.md — Hydrogen PDE Subnet Technical Specification

**Version:** 3.3 (Updated July 2026)
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

## 2. Scoring & Tracker

### 2.1 Multi-Objective Scoring (45/30/25)
Physics Fidelity, Robustness, Accuracy → combined score. Only new combined bests on a challenge receive strong weight.

### 2.2 Physics Gates
Hard gates (mass conservation, energy dissipation, boundary satisfaction, rollout stability, UQ calibration) and soft gates with multiplicative penalties. Phase-field specific gates also defined.

### 2.3 ChallengeWinnerTracker
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
- **Abaqus ODB / .fil Ingestion Pipeline** (miner submits `custom_data` with IPFS URI + checksum; validator parses and mixes with procedural data)
- Expanded symbolic regression track using **PySR** + DataDrivenDiffEq

### Phase 2: Multi-Physics Composition

**Coupling Framework: preCICE**

preCICE is selected as the primary coupling library for Phase 2 multi-physics challenges (FSI, CHT, Thermo-Elasticity). It is a mature, open-source partitioned coupling library designed for black-box multi-physics simulations. It provides implicit/explicit coupling, advanced data mapping, coupling acceleration, and strong language bindings (including Python).

**Integration Approach**:
- Specialists (e.g., `ns_2d`, `elasticity_2d`) are treated as black-box participants that implement the preCICE interface (or a thin Hydrogen adapter layer on top).
- The validator orchestrates the coupled simulation: starting specialist containers, initializing preCICE, managing data exchange/mapping/time-stepping/convergence, and evaluating the coupled result against physics gates.
- Two models are supported:
  - **Black-box preCICE**: Miners submit solvers that already speak the preCICE API (preferred for Phase 2A reference benchmarks).
  - **Hydrogen Adapter Layer**: A simplified interface that abstracts preCICE details for easier miner participation (target for Phase 2B+).

**Phase 2A — Verified Benchmarks (First 3–6 months)**
- FSI challenges (Turek/Hron 2D-1/2/3) using preCICE + OpenFOAM/CalculiX or equivalent reference solvers.
- Conjugate Heat Transfer (CHT) challenges with preCICE + OpenFOAM/PDEBench references.
- Three-track leaderboard: Monolith / Composition / Specialist-Only.
- preCICE is used to create credible, research-grade coupled reference cases.

**Phase 2B — Thermo-Elasticity**
- Generate ~48 Tier-1 mesh-converged references (varying β, κ, geometry) at 256^{2} using FEniCS monolithic or preCICE-partitioned approaches.
- Add thermo-elasticity challenges with `loss_vector` coupling terms.
- preCICE or custom coupling used depending on solver availability.

**Phase 2C — Variant Expansion**
- New Reynolds numbers, geometries, and coupling strengths on FSI/CHT/Thermo-elasticity.
- Specialist Bank grows; reuse rate target >80%.
- preCICE-based composition becomes the dominant submission pattern for multi-physics challenges.

**Rationale for preCICE**:
- Best matches the black-box specialist + composition vision.
- Mature ecosystem with validated reference cases.
- Good Python bindings and containerization support.
- Enables realistic, verifiable multi-physics benchmarks without Hydrogen having to implement coupling algorithms from scratch.
- Alternatives (MOOSE monolithic, custom Python coupling, FEniCS internal coupling) were evaluated; preCICE was selected for its partitioned black-box nature and research adoption.

### Phase 3: 3D Multi-Physics (Post-Turbulence Bridge)

**Phase 3.1** — 3D Turbulence Bridge (prerequisite)
- 3D Spectral Initialization Protocol
- Curriculum from 2D specialists → 3D
- `ns_3d_turbulent` specialist with verified k^(-5/3) spectrum
- 3D-specific stress gates (energy spectrum, Q-criterion, wall shear, Nu distribution)

**Phase 3.2** — 3D Multi-Physics Rollout
- 3D FSI, 3D Thermo-Elasticity, 3D CHT using preCICE (or evolved coupling layer) + appropriate 3D specialists and adapters.
- Same three-track leaderboard and stress testing applied.

**Phase 3.3** — Foundation Operator (LPM)
- Multi-teacher distillation across entire Specialist Bank (2D + 3D)
- FiLM conditioning on ProblemSignature + SymbolicMetadata
- Evidential UQ head
- Commercial fine-tuning API

---

## 5. Validator & Scoring Details

(Physics gates tables, multi-objective formula, ChallengeWinnerTracker behavior, and determinism requirements remain as previously defined.)

---

## 6. Future Domains

See `docs/FUTURE_DOMAINS.md` for the full analysis of additional domains (Electromagnetics, Photonics, Acoustics, Plasmas/Fusion, Quantum-informed modeling, etc.).

---

## 7. Current Limitations

- Abaqus ingestion pipeline and full Phase 1–3 roadmap (including preCICE-based multi-physics composition) are planned but not yet implemented.
- Hybrid emissions model is defined but not active.
- Landscape Agent, specialist distillation, and Symbolic Gauntlet are future work.
- Multi-validator consistency and canonical ranking not yet stress-tested.

---

*This specification reflects both current implementation and the planned phased roadmap.*
