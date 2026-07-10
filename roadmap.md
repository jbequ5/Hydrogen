# ROADMAP.md — Hydrogen Subnet Technical Roadmap

---

## Overview

This document defines the phased execution plan for Hydrogen, from launch through Foundation Operator. Each phase has clear entry/exit criteria, technical deliverables, and revenue milestones. Phases are sequential gates — not timeboxes. We advance when criteria are met.

---

## Phase 0: The Causal Baseline (Launch → Month 3)

### Objective
Establish the causal flywheel: miners submit strategies → validators verify with physics gates → Landscape distills causal knowledge → baseline improves.

### Scope: 10 Problems, Full PDE Taxonomy (2D + 3D Elliptic/Parabolic)

| # | Problem | Dimension | Physics Class | Reference Source |
|---|---------|-----------|---------------|------------------|
| 1 | Poisson | 2D | Elliptic, constant-coeff | PhysicsNeMo |
| 2 | Poisson | 3D | Elliptic, 3D scaling | PhysicsNeMo |
| 3 | Darcy | 2D | Elliptic, variable-coeff | PhysicsNeMo / PDEBench |
| 4 | Darcy | 3D | Elliptic, 3D hetero | PhysicsNeMo / PDEBench |
| 5 | Burgers | 2D | Nonlinear advection/shocks | PhysicsNeMo |
| 6 | Navier-Stokes | 2D | Incompressible, vorticity | PhysicsNeMo / JHTDB |
| 7 | Navier-Stokes | 3D | Low-Re laminar (Re≤100) | PhysicsNeMo |
| 8 | Heat | 2D | Transient, variable κ | PhysicsNeMo |
| 9 | Elasticity | 2D | Vector, tensor physics | PhysicsNeMo |
| 10 | Thermo-elasticity | 2D | **Multi-physics, loss_vector** | Generated (48 Tier 1 refs) |

### Technical Deliverables

**Validator Infrastructure**
- 5 pinned Docker images: `fno`, `pino`, `deeponet`, `gno`, `oformer` (PhysicsNeMo 24.09 + NeuralOperator 0.3.0, PyTorch 2.3, CUDA 12.4)
- Validation pipeline: train → public holdout eval → hidden stress test → physics gates → score
- Physics gates: mass (‖∇·u‖₁<1e-3), energy (dE/dt≤1e-4), boundary, rollout (100 steps), UQ calib (90% PI ∈ [0.88,0.92])
- Log-space improvement score: `log(E_baseline) - log(E_submission)`

**Miner Interface**
- Strategy JSON: backbone, loss_vector, optimizer, curriculum, UQ config, optional custom_data
- 0.1 TAO submission fee, 1 submission/challenge, last submission counts

**Landscape Agent (Owner-funded, 18% emissions + 10% time-locked treasury)**
- Fragment store: StrategyFragment (config, score, stress_pass, UQ, causal_parents)
- Daily DML causal update: `P(improvement | do(param))` per problem family
- Baseline proposal: updated JSON with strongest causal effects
- Fragment DAG with `causal_parents` lineage tracking

### Exit Criteria (All Required)
- [ ] Baseline log-improvement > 0.02/challenge averaged over 30 challenges
- [ ] ≥30 unique miners submitting
- [ ] ≥5 validators operational
- [ ] Landscape proposing baseline updates that improve next-challenge baseline
- [ ] All 10 problems have active competition

### Revenue at Phase 0 Exit
- **Asset:** Causal Knowledge Graph (500+ causally-validated interventions)
- **TAM:** $2-5M/yr licensing to NVIDIA/ANSYS/Siemens for "training best practices"
- **Revenue model:** API access to causal graph + baseline configs

---

## Phase 1: Adapters, Data Markets & Specialist Distillation (Months 3-6)

### Objective
Enable fine-grained innovation (adapters), reward data contribution, produce first verified specialists.

### New Miner Capabilities
- **LoRA adapters:** Rank-4-8 weight deltas applied to frozen backbone (`target_layers`, `rank`, `alpha`)
- **Custom datasets:** High-fidelity DNS, curated permeability fields, shock-capturing data
  - `data_uri` (IPFS), `checksum`, `usage` (augment/curriculum/label_only), `weight`
  - Encrypted submission option (landscape pubkey)

### Validator Updates
- Adapter application: load backbone → apply LoRA → train
- Custom data: download → checksum → optional decrypt → sanity probe → cache → mix per `usage`/`weight`
- Data royalty pool: 5% of emissions distributed by measured impact (Δerror when data added)

### Landscape Agent Extensions
- Adapter parameter correlation in DML
- Data impact measurement: `Impact = max(0, (E_without - E_with)/E_without)`
- **Specialist Distillation Pipeline (weekly):**
  1. Select top-K fragments per problem (score > 90th percentile, stress_passed)
  2. Multi-teacher distillation → Student (same backbone, 50% width)
  3. Loss: `α·Output_MSE + β·Physics_Loss + γ·Feature_Match + δ·UQ_Match`
  5. **Regression test:** Specialist MUST pass SAME stress tests as miners
  6. Publish ONNX + metadata + validity_domain + dual license (AGPL-3.0 + Commercial)

### Specialist Schema
```json
{
  "specialist_id": "darcy_2d_v3",
  "problem_signature": "...",
  "onnx_model": "...",
  "validity_domain": {"permeability_contrast": "≤10^4", "geometry": "structured"},
  "stress_test_results": {"mass": "pass", "energy": "pass", "rollout": "pass", "uq_calib": "pass"},
  "metrics_7d": {...},
  "license": "DUAL: AGPL-3.0 + Commercial",
  "provenance": ["fragment_id_1", "fragment_id_2", "..."]
}
```

### Exit Criteria
- [ ] ≥20 specialists in bank across ≥6 problem families
- [ ] Data royalty pool >5% of emissions
- [ ] Specialist reuse rate >80% (compositions use Bank specialists)
- [ ] ≥3 novel adapters with measurable impact (>5% improvement)

### Revenue at Phase 1 Exit
- **Asset:** Specialist Bank (20-30 verified ONNX specialists, dual-licensed)
- **TAM:** $10-50M/yr
  - Specialist licensing (AGPL-3.0 ecosystem + commercial dual-license)
  - Data royalties from custom datasets
  - Fine-tuning services on encrypted client data (TEE)

---

## Phase 2: Composition Engine & Specialist Marketplace (Months 6-18)

### Objective
Prove composition > monolith on multi-physics. Build composable specialist marketplace.

### Phase 2A: Verified Benchmarks Only (Months 1-3)
**Leverage existing verified 2D benchmarks — zero new data generation.**

| Problem | Source | Status | Specialist Pair |
|---------|--------|--------|-----------------|
| FSI 2D-1/2/3 | Turek/Hron | Verified, mesh-converged | `ns_2d` + `elasticity_2d` + `fsi_coupling` |
| CHT: Solid cooling / Electronic | PDEBench | Verified, mesh-converged | `ns_2d` + `heat_2d` + `cht_coupling` |

### Phase 2B: Thermo-Elasticity (Month 3)
**Only new data generation needed.** Generate 48 Tier 1 references (β×κ×geometry) at 256² with FEniCS monolithic, mesh-converged (3 levels). Cost: ~$3K.

### Phase 2C: Variant Expansion (Months 4-5)
New Re, geometries, coupling strengths on FSI/CHT/thermo-elasticity using existing references.

### Miner Submission (Phase 2)
```json
{
  "specialist_pipeline": [
    {"specialist_id": "ns_2d_v4", "role": "primary"},
    {"specialist_id": "heat_2d_v3", "role": "secondary"},
    {"adapter_id": "cht_coupling_v2", "role": "coupling"}
  ],
  "execution_schedule": "staggered",
  "max_coupling_iterations": 5,
  "coupling_tolerance": 1e-4
}
```

### Three-Track Leaderboard (Every Multi-Physics Challenge)
| Track | Submission | What It Proves |
|-------|------------|----------------|
| **Monolith** | Single strategy JSON (end-to-end) | Can monolith beat composition? |
| **Composition** | Specialist pipeline + adapter | Does composition beat monolith? |
| **Specialist-Only** | Single specialist (no adapter) | How much does adapter matter? |

**Same hidden stress test, same physics gates, three parallel leaderboards.**

### Phase 2C Exit Criteria (Go/No-Go for 3D)
| Metric | Target | If Missed |
|--------|--------|-----------|
| Composition win rate | >60% (Composition > Monolith) | Pivot: deepen single-physics specialists |
| Specialist reuse | >80% compositions use ≥1 Bank specialist | Extend Phase 1 |
| Adapter innovation | >30% novel adapters | Expand adapter design space |
| Stress test pass rate | >70% compositions pass | Coupling brittle → simplify adapter design |

### Revenue at Phase 2 Exit
- **Asset:** Composition Engine + Specialist Bank (50+ specialists, composable)
- **TAM:** $50-200M/yr
  - Specialist licensing (AGPL-3.0 + commercial)
  - Composition engine licensing (COMSOL, Ansys, Siemens)
  - Custom multi-physics pipelines for enterprise ($10M-100M contracts)

---

## Phase 3: The 3D Transition & Foundation Operator (Months 18+)

### Phase 3.0: 3D Single-Physics Foundations (Prerequisite)
**Before any 3D multi-physics, these MUST exist in Specialist Bank:**

| 3D Specialist | Source | Validation |
|---------------|--------|------------|
| `poisson_3d_v1` | Phase 0 3D Poisson | Stress test passed |
| `darcy_3d_v1` | Phase 0 3D Darcy | Stress test passed |
| `ns_3d_laminar_v1` | Phase 0 3D NS (Re≤100) | Stress test passed |
| `heat_3d_v1` | Phase 0 3D Heat | Stress test passed |
| `elasticity_3d_v1` | 2D→3D curriculum distillation | Stress test passed |
| `heat_3d_v1` | 2D→3D curriculum distillation | Stress test passed |

**Curriculum Distillation Protocol:**
```yaml
stage_1: zero_pad_fourier + noise(0.01), freeze backbone, train adapter (32³, 5 epochs)
stage_2: unfreeze last 2 spectral blocks, 64³, 20 epochs
stage_3: unfreeze all, 128³, 50 epochs, physics_informed + distillation_loss(teacher_2d)
stage_4: 128³ stress test validation + must_pass_2d_stress_tests_in_3d
```

### Phase 3.1: 3D Turbulence Bridge (Months 1-3) — CRITICAL PHASE
**2D NS does not prepare for 3D turbulence.** Dedicated phase to learn 3D turbulence from scratch.

| Week | Activity | Deliverable |
|------|----------|-------------|
| 1-2 | 3D Spectral Initialization Protocol | Proper 3D spectral init (not zero-pad) using 3D energy spectrum priors |
| 3-4 | 3D Turbulence Curriculum | Re=50→100→200→500 on channel/cylinder |
| 5-6 | 3D Turbulence Specialist | `ns_3d_turbulent_v1` with verified `k^(-5/3)` spectrum |
| 7-8 | 3D FSI Bridge | `ns_3d_turbulent` + `elasticity_3d` + FSI adapter |
| 9-10 | 3D Turbulence Stress Gates | Energy spectrum, Q-criterion, wall shear, Nu distribution |

**Gate:** `ns_3d_turbulent_v1` passes 3D turbulence stress tests → open 3D multi-physics.

### Phase 3.2: 3D Multi-Physics Rollout

| Phase | Challenges | Specialist Composition | Reference |
|-------|------------|------------------------|-----------|
| **3.2A** 3D FSI | Cylinder, flap, turbulent inflow | `ns_3d_turbulent` + `elasticity_3d` + `fsi_3d_adapter` | preCICE partitioned |
| **3.2B** 3D Thermo-Elasticity | Bimetal, engine block, turbine blade | `elasticity_3d` + `heat_3d` + `thermal_expansion_3d` | FEniCS monolithic |
| **3.2C** 3D CHT | Electronics, turbine cooling, battery | `ns_3d_turbulent` + `heat_3d` + `cht_3d_adapter` | OpenFOAM/COMSOL |

**Three-track leaderboard continues. Same stress test infrastructure.**

### Phase 3.3: Foundation Operator (LPM)
**Multi-teacher distillation across entire Specialist Bank (2D + 3D).**

```
LPM Architecture:
  Backbone: FNO/PINO hybrid (spectral + local kernels), 128 channels, 6 blocks
  Conditioning: ProblemSignature → FiLM layers modulate backbone
  UQ Head: Evidential (μ, σ, ν, α for Student-t)
  Router: Optional learned gating to specialist sub-networks

Training:
  L = Σ w_i · MSE(LPM(x; sig_i), Specialist_i(x))
    + λ_physics · PhysicsLoss(LPM)
    + λ_uq · UQ_Calibration_Loss
    + λ_consistency · CrossSpecialistConsistency
```

**Fine-tuning API (Commercial):**
```python
def fine_tune_lpm(client_encrypted_data, problem_signature):
    # 1. Decrypt in TEE (NVIDIA CC / AMD SEV)
    # 2. LoRA adapt (rank=8, 10-50 steps)
    # 3. Verify on client holdout + stress tests
    # 4. Return encrypted ONNX
```

---

## Revenue & TAM Summary by Phase

| Phase | Primary Asset | Revenue Streams | TAM | Timeline |
|-------|---------------|-----------------|-----|----------|
| **Phase 0** | Causal Knowledge Graph | Licensing to NVIDIA/ANSYS/Siemens | $2-5M/yr | Month 3 |
| **Phase 1** | Specialist Bank (20-30) | Licensing (dual), data royalties, fine-tuning API | $10-50M/yr | Month 6 |
| **Phase 2** | Composition Engine + Bank (50+) | Licensing, custom pipelines, enterprise contracts | $50-200M/yr | Month 12-18 |
| **Phase 3** | Foundation Operator (LPM) | API ($500-5K/model), custom surrogates ($50K-500K), enterprise platform | $1B+ | Year 2-3 |

---

## Risk Mitigation & Pivot Points

| Risk | Probability | Mitigation | Pivot Trigger |
|------|-------------|------------|---------------|
| 3D turbulence bridge fails | High | 2D composition thesis proven; 3D elliptic/parabolic specialists valuable | Pivot: double down on Phase 2 composition engine + elliptic/parabolic specialists |
| 3D reference costs exceed budget | Medium | Tiered fidelity (gold/silver/bronze); 2D→3D curriculum reduces training cost | Reduce 3D challenge frequency; focus on 2D/3D elliptic |
| Validator centralization (24GB+ GPU requirement) | Medium | Fee adjustment; validator emission increase; cloud validator program | Increase submission fee; validator emission share increase |
| Reference solver uncertainty | High | Tiered fidelity (gold/silver/bronze); cross-code verification for Tier 1 | Accept lower-fidelity stress tests; flag in metadata |
| Miner exodus | Low | Landscape has 500+ fragments → specialists → Foundation Operator survives | Emissions become "innovation bonus"; revenue from IP sustains |

---

## The Honest Summary

| Phase | Business Status | Technical Risk | Revenue Independence |
|-------|-----------------|----------------|----------------------|
| **Phase 0** | Proven flywheel, sellable asset | Low | ✅ Independent |
| **Phase 1** | Specialist marketplace, recurring revenue | Low | ✅ Independent |
| **Phase 2** | Composition engine, high-value IP | Medium (multi-physics benchmarks) | ✅ Independent of 3D |
| **Phase 3** | Moonshot (LPM) | **High (3D turbulence)** | ❌ Depends on 3D turbulence |

**The business is real at Phase 1. Profitable at Phase 2. Phase 3 is the 100x lottery ticket.**

**Build the flywheel. The moonshot is optional.**
