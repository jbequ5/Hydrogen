# SPEC.md — Hydrogen PDE Subnet Technical Specification v1.0

---

## 1. System Overview

### 1.1 Core Loop
```
Daily Challenge → Miner Strategy JSON → Validator Training → Physics-Gated Scoring → Landscape Causal Update → Next Baseline
```

### 1.2 Roles & Economics
| Role | Emission Share | Primary Function |
|------|----------------|------------------|
| Winner (post warm-up) | 41% | Highest verified improvement |
| Validators | 41% | Median consensus + physics-check completeness + UQ audit |
| Owner | 18% | Landscape Agent, Specialist Bank, Challenge Infra, Treasury (10% time-locked) |

**Submission fee:** 0.1 TAO (covers validator marginal cost ~0.08 TAO/run)

**Warm-up:** <10 distinct submissions/challenge → top 3 split 50/30/20  
**Competitive:** Winner-takes-all 41%

---

## 2. Miner Interface

### 2.1 Strategy JSON Schema
```json
{
  "backbone": "PINO",                    // Enum: FNO, PINO, DeepONet, GNO, OFormer
  "resolution": [128, 128, 64],          // Spatial grid [Nx, Ny, Nz]
  "pino": {                              // Backbone-specific config
    "loss_vector": {                     // Per-physics-term weights (required for multi-physics)
      "pde_residual": 1.5,
      "conservation": 0.8,
      "boundary": 0.5,
      "symmetry": 0.3,
      "coupling": 0.3                    // Thermo-elasticity coupling term
    },
    "physics_loss_type": "pde_residual", // Enum: pde_residual, conservation, symmetry
    "boundary_handling": "ghost_cells"   // Enum: ghost_cells, penalty, lagrange
  },
  "optimizer": "AdamW",
  "learning_rate": 0.001,
  "scheduler": "CosineAnnealingLR",
  "batch_size": 16,
  "epochs": 200,
  "physics_informed": true,
  "curriculum_learning": {
    "enabled": true,
    "start_resolution": [64, 64, 32],
    "end_resolution": [128, 128, 64],
    "ramp_epochs": 80
  },
  "uq_config": {
    "method": "deep_ensemble",           // Enum: deep_ensemble, conformal, evidential
    "num_members": 4,
    "calibration_target": 0.90
  },
  "custom_data": {                       // Optional
    "data_uri": "ipfs://...",
    "checksum": "sha256:...",
    "usage": "augment",                  // Enum: augment, curriculum, label_only
    "weight": 0.25
  }
}
```

### 2.2 Submission Rules
- **Fee:** 0.1 TAO (burned if validation fails pre-checks)
- **Format:** JSON only, ≤ 64 KB
- **Frequency:** 1 submission/miner/challenge (last submission counts)
- **Deadline:** 20 hours after challenge release (4-hour validation window)

---

## 3. Validator Specification

### 3.1 Backbone Images (Pre-built, Pinned)
| Image | Backbones | Base | PhysicsNeMo | NeuralOperator | PyTorch | CUDA |
|-------|-----------|------|-------------|----------------|---------|------|
| `hydrogen/validator:fno-v24.09` | FNO | nvcr.io/nvidia/pytorch:24.09-py3 | 24.09 | 0.3.0 | 2.3.0 | 12.4 |
| `hydrogen/validator:pino-v24.09` | PINO | same | same | same | same | same |
| `hydrogen/validator:deeponet-v24.09` | DeepONet | same | same | same | same | same |
| `hydrogen/validator:gno-v24.09` | GNO | same | same | same | same | same |
| `hydrogen/validator:oformer-v24.09` | OFormer | same | same | same | same | same |

**Hardware requirement:** NVIDIA GPU ≥ 24 GB VRAM (RTX 3090/4090/A100/H100). 3D NS at 128³ requires ~20 GB with gradient checkpointing.

### 3.2 Validation Pipeline (Deterministic)
```python
def validate_submission(challenge_id: str, miner_config: dict) -> ValidationResult:
    # 1. Load challenge data (public train/holdout, hidden stress test)
    train_data, holdout_data, stress_data = load_challenge_splits(challenge_id)
    
    # 2. Pull backbone image
    image = select_backbone_image(miner_config["backbone"])
    
    # 3. Inject config → train
    model = train_backbone(
        image=image,
        config=miner_config,
        train_data=train_data,
        custom_data=resolve_custom_data(miner_config.get("custom_data")),
        seed=derive_seed(challenge_id, validator_hotkey)
    )
    
    # 4. Evaluate on public holdout
    E_baseline = load_current_baseline_error(challenge_id)
    E_submission = evaluate(model, holdout_data)
    improvement = log(E_baseline) - log(E_submission)  # Log-space improvement
    
    # 5. Hidden stress test + physics gates
    stress_result = run_stress_test(model, stress_data, challenge_id)
    
    # 6. UQ calibration check
    uq_metrics = evaluate_uq(model, stress_data, miner_config["uq_config"])
    
    # 7. Compute score
    if stress_result.hard_failure:
        score = 0.0
        reason = stress_result.failure_reason
    else:
        base_score = max(0.0, improvement)
        soft_penalty = stress_result.soft_penalty  # ≤ 1.0
        uq_bonus = 0.05 if uq_metrics.calibrated else 0.0
        score = (base_score * soft_penalty) + 0.20 + uq_bonus  # Stress pass = +20%
    
    return ValidationResult(score, improvement, stress_result, uq_metrics)
```

### 3.3 Physics Gates (Stress Test)

#### Hard Gates (Score = 0 if failed)
| Check | Formula | Threshold | PDE Classes |
|-------|---------|-----------|-------------|
| **Mass Conservation** | `‖∇·u‖₁ / ‖u‖₁` | `< 1e-3` | NS, Darcy, Elasticity |
| **Energy Dissipation** | `dE/dt` | `≤ 1e-4` | NS, Heat, Burgers |
| **Boundary Satisfaction** | `‖u - u_BC‖₂ / ‖u_BC‖₂` | `< 1e-3` | All with BCs |
| **Rollout Stability** | `‖E(t=100) - E(t=0)‖ / E(t=0)` | `< 0.01` | All transient |
| **UQ Calibration** | `|coverage - 0.90|` | `< 0.02` | All (UQ mandatory) |

#### Soft Gates (Multiplicative Penalty)
| Check | Formula | Penalty Function |
|-------|---------|------------------|
| **Symmetry** | `‖u - u_flipped‖₂ / ‖u‖₂` | `max(0, 1 - 20 × (ratio - 0.05))` |
| **Spectral Fidelity** | `‖E_pred(k) - E_true(k)‖ / ‖E_true(k)‖` | `max(0, 1 - 10 × (error - 0.1))` |
| **Conservation Drift** | `‖dM/dt‖` | `max(0, 1 - 100 × drift)` |

**PDE-Specific Stress Floors** (baseline_stress_error × 0.9 floor):
| PDE Class | Mass Cons | Energy Diss | Rollout | UQ Cal |
|-----------|-----------|-------------|---------|--------|
| Poisson/Darcy | 1e-4 | N/A | N/A | 0.02 |
| Burgers | 1e-3 | 1e-3 | 0.02 | 0.03 |
| NS (Re≤100) | 1e-3 | 1e-3 | 0.01 | 0.02 |
| Heat | N/A | 1e-4 | 0.01 | 0.02 |
| Elasticity | 1e-3 | N/A | N/A | 0.02 |
| Thermo-elasticity | 1e-3 | 1e-4 | 0.02 | 0.03 |

### 3.4 Scoring Formula
```
If hard_failure: score = 0.0
Else:
    base_improvement = max(0, log(E_baseline) - log(E_submission))
    soft_penalty = Π(soft_gate_penalties)  ∈ [0, 1]
    stress_bonus = 0.20  (fixed for passing all hard gates)
    uq_bonus = 0.05 if UQ calibrated else 0.0
    score = (base_improvement * soft_penalty) + stress_bonus + uq_bonus
```

### 3.5 Consensus
- Each validator submits `score`, `improvement`, `stress_passed`, `uq_calibrated`
- Chain computes **median** of validator scores
- Validators with `|score - median| > 0.1` flagged for audit
- 3+ validators required per challenge

---

## 4. Challenge Specification

### 4.1 Phase 0 Problem Suite (10 Problems)

| ID | Problem | Resolution | Train Split | Holdout | Stress Variants |
|----|---------|------------|-------------|---------|-----------------|
| 1 | 2D Poisson | 128×128 | 800 | 200 | Resolution 64/256, forcing freq |
| 2 | **3D Poisson** | **64×64×64** | **400** | **100** | **Resolution 32/128, anisotropy** |
| 3 | 2D Darcy | 128×128 | 800 | 200 | Permeability contrast 10³, log-normal |
| 4 | **3D Darcy** | **64×64×64** | **400** | **100** | **Contrast 10⁴, channelized fields** |
| 5 | 2D Burgers | 256×100 (x,t) | 800 | 200 | ν ∈ [0.001, 0.1], shock formation |
| 6 | 2D NS (vorticity) | 128×128 | 800 | 200 | Re ∈ [10, 500], forcing spectrum |
| 7 | **3D NS (low-Re)** | **64×64×32** | **400** | **100** | **Re ∈ [10, 100], 3D forcing** |
| 8 | 2D Heat (κ(x,y)) | 128×128×50 (x,y,t) | 800 | 200 | κ contrast 10³, time horizon |
| 9 | 2D Elasticity | 128×128 | 800 | 200 | λ/μ contrast, mixed BCs, locking test |
| 10 | 2D Thermo-Elasticity | 128×128×50 | 400 | 100 | Coupling β ∈ [0.1, 1.0], transient |

**Data sources:** PDEBench, JHTDB, PhysicsNeMo examples, procedural generation (seeded by challenge_id)

### 4.2 Challenge Generation (Deterministic)
```python
def generate_challenge(challenge_id: str, problem_id: int) -> Challenge:
    seed = hash(challenge_id + str(problem_id))
    rng = np.random.default_rng(seed)
    
    # Public splits (fixed per problem)
    train, holdout = load_fixed_splits(problem_id)
    
    # Hidden stress test (procedural)
    stress = generate_stress_test(problem_id, rng)
    
    # Baseline config (from Landscape)
    baseline = get_current_baseline(problem_id)
    
    return Challenge(
        challenge_id=challenge_id,
        problem_id=problem_id,
        train_data=train,
        holdout_data=holdout,
        stress_data=stress,
        baseline_config=baseline,
        submission_deadline=now() + 20_hours,
        stress_floors=get_stress_floors(problem_id)
    )
```

---

## 5. Landscape Agent Specification

### 5.1 Data Model
```protobuf
message StrategyFragment {
  string fragment_id = 1;              // SHA256(config_json + challenge_id + timestamp)[:16]
  int32 miner_uid = 2;
  string challenge_id = 3;
  int32 problem_id = 4;
  string config_json = 5;
  float improvement = 6;               // log(E_baseline) - log(E_submission)
  bool stress_passed = 7;
  UQMetrics uq_metrics = 8;
  float score = 9;
  uint64 timestamp = 10;
  repeated string causal_parents = 11; // Fragment IDs this derived from
  map<string, float> param_values = 12; // Flattened config for analysis
}

message UQMetrics {
  float calibration_error = 1;         // |coverage - target|
  float sharpness = 2;                 // Mean prediction interval width
  float coverage = 3;                  // Empirical coverage
  bool calibrated = 4;                 // |coverage - 0.90| < 0.02
}
```

### 5.2 Daily Causal Update (Post-Challenge)
```python
def daily_causal_update(new_fragments: List[StrategyFragment]):
    # 1. Add to fragment DAG
    dag.add_nodes(new_fragments)
    
    # 2. Estimate causal effects per problem family
    for problem_id in PROBLEM_FAMILIES:
        problem_fragments = dag.get_problem_fragments(problem_id)
        
        # Double Machine Learning for heterogeneous treatment effects
        # Y = improvement, T = config_param, X = other_params + problem_context
        dml = DoubleML(
            model_y=RandomForestRegressor(),
            model_t=RandomForestRegressor(),
            n_folds=5
        )
        dml.fit(problem_fragments)
        
        # Estimate ATE for each tunable parameter
        effects = {}
        for param in TUNABLE_PARAMS:
            effects[param] = dml.ate(param)
        
        # Conditional effects: "fourier_modes helps when physics_loss > 1.0"
        interactions = dml.interaction_effects()
        
        # 3. Propose baseline update
        proposal = propose_baseline(effects, interactions, current_baseline)
        owner_review_queue.put(proposal)
```

### 5.3 Weekly Specialist Distillation
```python
def weekly_distillation():
    for problem_id in PROBLEM_FAMILIES:
        # 1. Select top-K fragments (score > 90th percentile, stress_passed)
        teachers = select_top_fragments(problem_id, k=5)
        
        # 2. Distill into student (same backbone, 50% width)
        student = distill_ensemble(
            teachers=teachers,
            student_config=StudentConfig(width_factor=0.5),
            loss_fn=DistillationLoss(
                alpha_output=1.0,      # Output MSE
                alpha_physics=0.5,     # Physics loss on student
                alpha_features=0.3,    # Feature matching
                alpha_uq=0.2           # UQ matching
            ),
            data=load_problem_data(problem_id)
        )
        
        # 3. Regression test: specialist must pass same stress tests
        stress_result = run_stress_test(student, get_stress_data(problem_id))
        if stress_result.hard_failure:
            log_failure("Distilled specialist failed stress test")
            continue
        
        # 4. Export ONNX + metadata
        specialist = Specialist(
            specialist_id=f"{problem_id}_v{version}",
            onnx_model=export_onnx(student),
            problem_signature=get_signature(problem_id),
            metrics=evaluate_full(student, problem_id),
            validity_domain=estimate_validity_domain(student, problem_id),
            license="AGPL-3.0 + Commercial Dual-License"
        )
        specialist_bank.publish(specialist)
```

### 5.4 Landscape Treasury & Governance
- **Funding:** 18% Owner emissions + 10% time-locked (6-month cliff, 2-year vest)
- **Multi-sig:** 3/5 (Owner, Lead Validator, Lead Researcher, Community Rep, Legal)
- **Spending:** Agent compute, specialist distillation GPU, challenge generation, audits
- **Audit:** Quarterly public report of Landscape Treasury spend + causal graph snapshots

---

## 6. Specialist Bank & Marketplace

### 6.1 Specialist Metadata
```protobuf
message Specialist {
  string specialist_id = 1;           // e.g., "navier_stokes_2d_v3"
  string problem_signature = 2;       // Hash of ProblemSignature protobuf
  bytes onnx_model = 3;               // ONNX model bytes
  Metrics7D metrics = 3;              // fidelity, accuracy, efficiency, ...
  ValidityDomain validity = 4;        // PDE params where specialist works
  repeated string known_failures = 5; // e.g., "fails at Re>500"
  License license = 6;                // DUAL: AGPL-3.0 + Commercial
  uint64 created_at = 7;
  string distilled_from = 8;          // Fragment IDs of teachers
}
```

### 6.2 Miner Usage (Phase 2+)
```json
{
  "specialist_id": "navier_stokes_2d_v3",
  "adapter": {                        // Optional micro-tuning
    "type": "lora",
    "rank": 4,
    "target_layers": ["pino_layers.3"]
  }
}
```
Validator loads ONNX → runs inference on holdout + stress test → scores.

### 6.3 Licensing Model
- **AGPL-3.0:** Free for research, open-source, internal use
- **Commercial License:** Per-seat or per-inference API, includes:
  - Indemnification
  - SLA (uptime, latency)
  - Fine-tuning support on private data
  - Validity domain extension consulting

---

## 7. Foundation Operator (Phase 3+)

### 7.1 Architecture
- **Backbone:** FNO/PINO hybrid (spectral + local kernels)
- **Width:** 128 channels, 6 spectral blocks
- **Conditioning:** ProblemSignature → FiLM layers modulate backbone
- **UQ:** Built-in evidential head (outputs μ, σ, ν, α for Student-t)

### 7.2 Training
```
Multi-teacher distillation from Specialist Bank:
  L = Σ w_i * MSE(foundation(x), specialist_i(x)) 
    + λ_physics * PhysicsLoss(foundation)
    + λ_uq * UQ_Calibration_Loss
    + λ_consistency * CrossSpecialistConsistency
```
**Data:** Union of all specialist training data + synthetic ProblemSignature sampling

### 7.3 Fine-Tuning API (Commercial)
```python
def fine_tune_foundation(client_data: EncryptedBlob, problem_signature: ProblemSignature) -> Specialist:
    # 1. Decrypt in TEE (NVIDIA CC / AMD SEV)
    data = tee_decrypt(client_data)
    
    # 2. Few-shot adaptation (10-50 steps, LoRA rank=8)
    adapted = lora_adapt(foundation, data, steps=20)
    
    # 3. Verify on client holdout (if provided) + stress tests
    if not verify(adapted, problem_signature):
        raise AdaptationFailed
    
    # 4. Return encrypted ONNX
    return tee_encrypt(export_onnx(adapted))
```

---

## 8. Consensus & Slashing

### 8.1 Validator Slashing Conditions
| Offense | Evidence | Slash |
|---------|----------|-------|
| Score deviation > 0.15 from median (3+ consecutive) | On-chain scores | 5% stake |
| Missed validation deadline (3+ consecutive) | Missed block window | 2% stake |
| Failed reproducibility audit | Auditor rerun ≠ submitted score | 10% stake |
| Physics check manipulation | Auditor finds disabled checks | 20% stake + ban |

### 8.2 Miner Penalties
| Offense | Penalty |
|---------|---------|
| Invalid JSON / schema violation | 0.1 TAO fee burned |
| Custom data checksum mismatch | 0.1 TAO fee burned |
| Spam (>5 submissions/challenge) | 24hr submission cooldown |

---

## 9. Implementation Checklist

### Phase 0 (Launch)
- [ ] 5 backbone Docker images built & tested
- [ ] 10 challenge datasets generated + stress floors calibrated
- [ ] Validator pipeline: train → evaluate → stress test → score
- [ ] Miner CLI: submit JSON, pay fee, query results
- [ ] Chain pallet: challenge management, scoring consensus, emissions
- [ ] Landscape Agent: fragment store, DML causal inference, baseline proposer
- [ ] Dashboard: live leaderboard, fragment explorer, causal graph

### Phase 1 (Month 2-3)
- [ ] LoRA adapter support in validator
- [ ] Custom data ingestion + caching + data royalty pool
- [ ] Specialist distillation pipeline (ONNX export + regression test)
- [ ] Dual-license legal framework

### Phase 2 (Month 4-6)
- [ ] Specialist Bank on-chain registry
- [ ] Miner specialist selection pathway
- [ ] Foundation Operator multi-teacher distillation
- [ ] Commercial fine-tuning API (TEE integration)

---

## 10. Appendix: Mathematical Definitions

### 10.1 Log-Space Improvement
```
improvement = log(E_baseline) - log(E_submission)
where E = relative L2 error = ‖u_pred - u_true‖₂ / ‖u_true‖₂
```
*Properties:* Rewards consistent orders-of-magnitude improvement; invariant to baseline magnitude.

### 10.2 Double Machine Learning (DML) for Causal Effects
```
Y = improvement, T = target_param, X = other_params + context
1. Regress Y ~ X → Ŷ, regress T ~ X → T̂
2. Residuals: Ỹ = Y - Ŷ, T̃ = T - T̂
3. ATE = E[Ỹ * T̃] / E[T̃²]
4. Heterogeneous effects: τ(x) = E[Ỹ | X=x] / E[T̃ | X=x]
```
*Robust to:* High-dimensional X, non-linear relationships, partial confounding.

### 10.3 UQ Calibration Metric
```
calibration_error = |(1/N) Σ 1{y ∈ PI_α(x)} - (1-α)|
sharpness = (1/N) Σ width(PI_α(x))
```
*Target:* calibration_error < 0.02 at α=0.90

---

*End of SPEC.md v1.0*
