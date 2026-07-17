# ROADMAP.md — Hydrogen Subnet Technical Roadmap (Updated post-cleanup)

**Note**: This roadmap has been lightly aligned with the consolidated SPEC.md. Phase 0 scope reduced to 3 PDEs for rapid, high-signal iteration on the core flywheel (reproducibility, physics gates, causal inference, incentives). Full 7-PDE scope and later phases remain the vision but are now explicitly gated.

---

## Phase 0: The Physics Flywheel (Launch → Month 3) — CURRENT FOCUS

**Objective**: Ship a working, autonomous causal flywheel with hard physics gates, reproducible validation, and measurable baseline improvement.

**MVP Scope**: 3 PDEs (Poisson 2D, Darcy 2D, Burgers). PyTorch/PhysicsNeMo only. Pre-computed symbolic metadata. Basic Landscape (DML or strong causal analysis). Miner CLI + SDK. 3+ validators.

**Key Deliverables**:
- Pinned validator Docker image(s) with deterministic harness.
- Challenge data pipeline + hidden stress test generator (seeded).
- Physics gate evaluators (boundary, rollout, UQ; mass/energy for relevant PDEs).
- Miner strategy submission + local validation helper.
- Landscape: fragment ingestion → causal effects → baseline proposals.
- Emission mechanics prototype (top-4 split + bonuses).
- Structured feedback to miners/agents.

**Exit Criteria**:
- Baseline log-improvement > 0.02/challenge avg over 30 epochs.
- ≥10 unique miners, ≥3 validators.
- Landscape updates measurably improve subsequent baselines.
- All components reproducible and auditable.

**Revenue at Exit**: Causal knowledge graph asset (training best practices). Licensing potential to NVIDIA/ANSYS/etc.

---

## Phase 1: Specialist Bank & Data Markets (Post Phase 0)

Add LoRA, custom datasets (Abaqus ingestion), data royalties (5% pool), 20-30 verified ONNX specialists with symbolic metadata preserved, dual licensing.

---

## Phase 2: Composition Engine & Marketplace

Multi-physics verified benchmarks first (FSI, CHT, thermo-elasticity). Six-track leaderboards. Composition > monolith proof. Go/No-Go gate for 3D.

---

## Phase 3: 3D + Foundation Operator + Edge HIL

3D single-physics foundations → turbulence bridge (critical, high risk) → multi-physics rollout → LPM Foundation Operator with TEE fine-tuning + edge deployment (Jetson, FPGA, PLC).

**Risk Note**: 3D turbulence bridge is a significant research effort. Success here gates the highest-TAM vision.

---

See consolidated SPEC.md for technical details and Launch_Spec.md (legacy) for earlier Phase 0 elaboration. Appendices contain runtime specifics.

*Prioritize shipping the flywheel. Everything else compounds from there.*