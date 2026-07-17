# SPEC.md — Hydrogen Technical Specification (Consolidated, Phase 0 MVP Focus) v2.5

**Status**: Deduplicated and aligned from previous Sepc.md / Launch_Spec.md versions. Removed repeated SciML dependency blocks, duplicated Phase 1 descriptions, and section numbering artifacts. Full historical detail preserved in git history and Appendices/. This is the single source of truth going forward.

---

## 1. System Overview & Core Loop

Hydrogen is a Bittensor subnet that turns physics simulation into a compounding, incentive-aligned knowledge economy.

**Core Loop (Phase 0 MVP)**:
```
Challenge released (PDE + train/holdout/stress + symbolic metadata)
  → Miners submit strategy JSON (backbone, loss_vector, curriculum, UQ, optional custom_data)
  → Validators (pinned Docker) train on public split → evaluate holdout → run hidden stress test
  → Hard physics gates (binary pass/fail) → Score = log(E_baseline) - log(E_submission)
  → Median consensus across ≥3 validators
  → Top-4 emissions (40/30/20/10) + novelty/symbolic bonuses
  → Every fragment → Landscape Agent (Double ML causal inference on DAG)
  → Daily baseline update proposal + weekly specialist distillation (top-K → ONNX)
```

**Roles & Economics (Phase 0)**:
- Top 4 miners per challenge: 40/30/20/10 split of challenge budget (improvement > 0 required).
- Validators: ~41% share for reliable physics gating + UQ audit + consensus participation.
- Owner/Landscape: 18% + time-locked treasury for agent compute, distillation, infra.
- Submission fee: 0.1 TAO (burned on pre-check failure).
- Novelty bonus + symbolic bonus gated on measurable improvement.

**Hard Physics Gates (Phase 0 — start simple)**:
- Boundary satisfaction: ‖u - u_BC‖_{2} / ‖u_BC‖_{2} < 1e-3
- Rollout stability (100 steps): ‖E(t=100) - E(0)‖ / E(0) < 0.01
- UQ calibration (90% PI coverage): |coverage - 0.90| < 0.02
- Mass conservation & energy dissipation added for relevant PDEs (NS, Burgers, etc.)

Hard failure → score = 0. Physics is binary.

---

## 2. Supported Backends & Tooling (Tiered, Phase 0 Starts Simple)

**Phase 0 MVP (Ship first)**: PyTorch + PhysicsNeMo + NeuralOperator (pinned `hydrogen/validator:pino-v0.1` image). Deterministic flags + fixed seeds.

**Later tiers** (post-MVP):
- JAX (jNO/Equinox)
- Julia/SciML (NeuralOperators.jl + Lux + ModelingToolkit.jl) via juliacall or sidecar

Cross-framework validation via ONNX where possible.

**Symbolic Layer (Phase 0 MVP)**: Pre-computed JSON metadata per challenge (generated offline with ModelingToolkit.jl principles or rules). Contains symmetries, conservation laws, dimensionless groups, suggested loss weights, boundary types, validity domain. Used for auto loss weighting in miner strategies and adaptive gate thresholds.

Full runtime MTK integration and acausal composition deferred to Phase 1+.

---

## 3. Miner Interface

Strategy JSON schema (Phase 0):
```json
{
  "challenge_id": "poisson_2d_v1",
  "hotkey": "5F...",
  "backbone": "PINO",
  "resolution": [128, 128],
  "pino": {
    "loss_vector": { "pde_residual": 1.0, "conservation_mass": 1.5, "boundary": 0.5 },
    "physics_loss_type": "pde_residual",
    "boundary_handling": "ghost_cells"
  },
  "optimizer": "AdamW",
  "learning_rate": 0.001,
  "curriculum_learning": { "enabled": true, "start_resolution": [64, 64], "end_resolution": [128, 128], "ramp_epochs": 50 },
  "uq_config": { "method": "deep_ensemble", "num_members": 4, "calibration_target": 0.90 }
}
```

Miners pay 0.1 TAO fee. Last submission per challenge counts. No weights uploaded.

---

## 4. Validator Specification

Pinned Docker images with PhysicsNeMo, deterministic PyTorch settings, and physics gate evaluators.

Validation pipeline (high level):
1. Load challenge splits + symbolic metadata.
2. Train / configure backbone per strategy JSON (seed = derive_seed(challenge_id, validator_hotkey)).
3. Evaluate on public holdout.
4. Run hidden stress test (procedural + The Well slices where applicable).
5. Apply hard + soft physics gates.
6. Compute score and UQ metrics.
7. Return result for median consensus.

Reproducibility note: Strict seeds + `torch.use_deterministic_algorithms(True)`. Tolerance bands or canonical cloud instances recommended for consensus edge cases. Full training logs + model hash for auditability.

---

## 5. Challenge Specification (Phase 0 MVP: 3 PDEs)

| ID | Problem | Dim | Physics | Reference |
|----|---------|-----|---------|-----------|
| 1 | Poisson | 2D | Elliptic | PhysicsNeMo |
| 2 | Darcy | 2D | Elliptic, variable coeff | PhysicsNeMo / PDEBench |
| 3 | Burgers | 1D/2D | Nonlinear advection/shocks | PhysicsNeMo |

Each provides: public train/holdout, hidden stress test (seeded procedural + Well slices), symbolic metadata JSON.

Stress test generation: Deterministic from challenge_id. Includes parameter/geometry shifts + curated Well dataset slices mapped per PDE family.

---

## 6. Landscape Agent

- Ingests every StrategyFragment (config, score, stress_pass, UQ, lineage).
- Daily: Double ML (econml/dowhy or HistGradientBoosting) on fragment DAG per problem family → causal effects + interactions → baseline proposal.
- Weekly: Top-K distillation → ONNX specialists (regression-tested on same stress tests) → publish to Specialist Bank with validity domain + symbolic metadata.
- Initially owner-operated / funded. Storage: Parquet + lightweight DB or IPFS-backed.

---

## 7. Emission & Incentive Mechanics (Phase 0)

Challenge budget = total_subnet_emission / min(active_challenges, 10).

Top-4 split (improvement > 0): 40% / 30% / 20% / 10%.
Novelty bonus (5%, improvement-gated) + symbolic bonus (2%, >5% improvement).
Bounty accumulation until breakthrough.
Validators paid for completeness + physics audit reliability.

See roadmap.md for full phased economics and risk mitigations.

---

## 8. Phase 0 MVP Exit Criteria (Ship These First)

- 3 PDE challenges live with reproducible data + symbolic metadata.
- ≥3 operational validators on pinned images.
- ≥10 unique miners submitting.
- Baseline log-improvement > 0.02/challenge averaged over 30 epochs.
- Landscape producing causal baseline updates that measurably improve next round.
- Working miner CLI + Python SDK with local validation helper.
- Deterministic validation harness + audit logs.

---

## 9. Later Phases (High-Level References)

Phase 1: LoRA adapters, custom data (incl. Abaqus ODB/fil ingestion), data royalties, 20-30 specialists in Bank, symbolic metadata preservation in distillation.

Phase 2: Multi-physics (FSI, CHT, thermo-elasticity) with six-track leaderboards (Monolith / Composition / Specialist-Only / Symbolic tracks). Go/No-Go for 3D.

Phase 3: 3D foundations → turbulence bridge → multi-physics rollout → Foundation Operator (LPM) with TEE fine-tuning API + edge HIL deployment.

Full details on composition, agent swarms (DID/A2A/reputation/slashing), Specialist Bank marketplace, and edge codegen (MTK → CUDA/VHDL) are in roadmap.md and historical appendices. These are explicitly deferred until Phase 0 flywheel spins autonomously.

---

## 10. Open Technical Questions & Mitigations (Being Addressed in Scaffolding)

- Reproducibility across heterogeneous GPUs → tolerance + canonical images + audit logs.
- Julia interop in Docker → start with pre-computed metadata; add juliacall/sidecar post-MVP.
- Bittensor custom emission split & fees → standard UID scoring + post-processing layer or custom reward function in initial implementation.
- Data hosting → HF Datasets + CDN for core; IPFS for custom miner data.

---

*End of consolidated SPEC.md v2.5. Previous duplicated content removed for maintainability. Historical versions in git.*