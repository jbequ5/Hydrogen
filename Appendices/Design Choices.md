# Carbon Subnet Design Review
**Founder → Tech Lead Discussion**  
*Walking through the design, exposing trade-offs, getting your eyes on implementation*

---

## 1. SYSTEM ARCHITECTURE — HIGH LEVEL FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CARBON SUBNET                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MINER / AGENT                                                              │
│  ├─ Strategy JSON (loss config, curriculum, architecture)                  │
│  ├─ MCP Interface                                                          │
│  │   ├─ Estimation Mode (near-zero cost, noisy prior anchored)             │
│  │   ├─ Light Training Mode (local, reduced budget)                        │
│  │   └─ Full Submission (validator trains + evaluates)                     │
│  └─ Miner Toolkit (Docker + Python SDK)                                    │
│          │                                                                  │
│          ▼                                                                  │
│  VALIDATOR (5+ for consensus)                                               │
│  ├─ Trustless Data Generation (procedural, seeded by block hash)           │
│  ├─ Multi-Fidelity Pipeline                                                 │
│  │   ├─ Tier 1: Fast stress filter (cheap, eliminates weak)               │
│  │   └─ Tier 2: Full hidden adversarial + physics gates                   │
│  ├─ Online physics residual monitoring (adaptive loss re-weighting)        │
│  └─ Model Card Generator (full provenance + diagnostics)                   │
│          │                                                                  │
│          ▼                                                                  │
│  LANDSCAPE AGENT (Compounding Intelligence)                                 │
│  ├─ PySR → Symbolic constraints (conservation laws, symmetries)            │
│  ├─ Double ML → Causal effects (strategy choice → robustness)              │
│  ├─ ModelingToolkit.jl → Structured loss terms                             │
│  ├─ Specialist Bank (distilled reusable components)                        │
│  └─ Noisy Priors → distributed back to miners                              │
│          │                                                                  │
│          ▼                                                                  │
│  EMISSIONS (Yuma Consensus + ChallengeWinnerTracker)                       │
│  ├─ 41% Miners (score-weighted, exponential decay)                         │
│  ├─ 41% Validators (→ TAO-α pool → staker yield)                           │
│  └─ 18% Team/Treasury (ops, liquidity, R&D)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CORE DESIGN CHOICES — WHAT & WHY

### 2.1 Trustless Verification: Procedural Generation + Public Seeding

| **What** | All evaluation data generated at runtime from open-source generator. Seed = `hash(challenge_id + block_hash + run_nonce)`. |
|----------|--------------------------------------------------------------------------------------------------------------------------|

| **Why Not Alternatives** |
|--------------------------|
| ❌ Fixed test sets → miners overfit, leakage inevitable |
| ❌ Centralized hidden data → "trust us" not credible for engineering |
| ❌ zkML proofs → too slow for PDE training loops |
| ❌ Committee voting → subjective, no physics grounding |

| **Key Properties** |
|--------------------|
| ✅ **Auditable**: Anyone can run generator with same seed → same data |
| ✅ **Unpredictable**: Block hash not known in advance |
| ✅ **Fresh every run**: New stress variants each evaluation |
| ✅ **Scientifically justified**: Parameter ranges documented with physics references (Sec 9 of TRUSTLESS_VERIFICATION.md) |
| ✅ **Validated**: Generator outputs periodically checked against FEniCS/OpenFOAM |

| **Phase 0 → Phase 1 Upgrade** |
|-------------------------------|
| Phase 0: `challenge_id + block_hash` (all validators grade same instances) |
| Phase 1: Commit-reveal + drand beacon (stronger collusion resistance) |

---

### 2.2 Physics Gates as Hard Constraints (Zero Score on Violation)

| **What** | 5 hard gates. Violate any → score = 0. No soft penalties. |
|----------|-----------------------------------------------------------|

| **The 5 Gates** |
|-----------------|
| 1. **Mass Conservation** — divergence-free, continuity residual |
| 2. **Energy Stability** — dissipation ≤ input + numerical tolerance |
| 3. **Boundary Satisfaction** — Dirichlet/Neumann/Periodic BCs met |
| 4. **Rollout Stability** — 1000+ steps no blowup under perturbation |
| 5. **UQ Calibration** — prediction intervals cover truth at stated confidence |

| **Why Hard Gates** |
|--------------------|
| Soft penalties → optimizer finds "sweet spot" violating physics slightly |
| Hard gates → **forces genuine physics compliance** |
| Binary = **auditable for certification** (regulators understand pass/fail) |
| Tunable weights = gameable; binary = not |

| **Scoring (Only If ALL Gates Pass)** |
|--------------------------------------|
| Physics Fidelity: 45% (residuals, conservation, boundaries, stability) |
| Robustness: 30% (hidden stress, rollout, OOD generalization, UQ) |
| Accuracy: 25% (holdout MSE, relative L2, spectral error) |

---

### 2.3 Three-Tier Miner Participation (Submission Always Free)

| **Core Philosophy** | Validator *always* does full training + hidden evaluation. Local training optional. |
|---------------------|-------------------------------------------------------------------------------------|

| Tier | Compute | Anchored To | Purpose | Required? |
|------|---------|-------------|---------|-----------|
| **Estimation Mode** | Near-zero | Noisy Prior | Rapid screening, agent-friendly | No |
| **Light Training** | Low (1-4 GPU hrs) | Noisy Prior | Main iteration loop | No (recommended) |
| **Full Submission** | Network-paid | Hidden data | Official score + emissions | Yes |

| **Critical Separation** |
|-------------------------|
| Local loops use **different seeds / different stress variants** than validator |
| Miners **never** see validator's hidden test data or full stress set |
| Prevents gaming official evaluation by tuning locally |
| Light Training *can* apply physics gates for signal — but doesn't replace official |

| **Estimation Mode Details** |
|----------------------------|
| Linear/sensitivity approximation around noisy prior |
| Optional small proxy model |
| Returns: estimated delta, confidence, risk flags |
| Clearly labeled "estimate" — not substitute for training |

---

### 2.4 Landscape Agent — Compounding Intelligence Flywheel

| **What** | Post-hoc analysis of ALL Model Cards → symbolic + causal insights → better priors for miners |
|----------|------------------------------------------------------------------------------------------------|

| **Pipeline** |
|--------------|
| **1. Symbolic Regression (PySR)** |
| Input: Strategy features + gate outcomes + stress results |
| Output: Conservation laws, symmetries, invariants as equations |
| → ModelingToolkit.jl → Structured, differentiable loss terms |
| |
| **2. Causal Inference (Double ML)** |
| Treatment: Strategy choices (loss weights, curriculum, architecture) |
| Outcome: Robustness score / gate pass |
| Confounders: Physics class, data seed, backbone |
| Output: Causal effects — "Do(X) improves Y" |
| |
| **3. Knowledge Base Update** |
| Noisy priors (perturbed best strategies) → miners |
| Strategic guidance (causal insights, redacted) → miners |
| Specialist distillation → reusable modules |
| Challenge design → next phase physics classes |

| **Why This Matters** |
|----------------------|
| Centralized teams learn linearly (quarterly retrospectives) |
| Carbon learns **per block** — every evaluation improves the collective |
| Specialist Bank = reusable components across physics classes |
| **Moat**: Raw causal graphs + DML outputs stay protected; only distilled guidance shared |

---

### 2.5 Challenge Progression — Phased Physics Complexity

| Phase | Timeline | Physics Scope | Revenue Unlock |
|-------|----------|---------------|----------------|
| **Phase 0** | Months 0-6 | 7 single-physics PDEs (Poisson, Darcy, Burgers, NS-laminar, Heat, Elasticity, Thermo-Elasticity) | Tier 1 Model Zoo: 7 certified specialist families |
| **Phase 1** | Months 6-12 | Same 7 + custom datasets, LoRA, Abaqus ingestion | Tier 2/3 Sponsored Challenges ($150k-800k) |
| **Phase 2** | Months 12-18 | Multi-physics: FSI (Turek/Hron), CHT, Thermo-Elasticity + preCICE | High-value coupled surrogates |
| **Phase 3** | Months 18-30 | 3D + turbulence, 3D-specific gates, curriculum from 2D specialists | Production digital twin surrogates |

| **Why Phased** |
|----------------|
| Validator complexity incremental |
| Miner onboarding progressive |
| **Tier 1 revenue at Phase 0** — don't wait for multi-physics |
| Gate calibration per physics class (not all at once) |

---

### 2.6 Tokenomics — Fixed, Immutable, dTAO-Native

| **Emission Schedule** |
|-----------------------|
| 21M α hard cap, halvings ~4 years |
| 14,400 α/day (Year 1) → 7,200 (2027) → 3,600 (2031) → 1,800 (2035) |

| **Split (Per Block, Immutable)** |
|----------------------------------|
| **41% Miners** — Score-weighted via ChallengeWinnerTracker (exponential decay) |
| **41% Validators** → Deposit to TAO-α pool automatically |
| **18% Team/Treasury** — Ops, liquidity, R&D, grants (earned daily, no cliff) |

| **TAO-α Pool (Investor Yield)** |
|---------------------------------|
| Validators deposit α → pool |
| TAO lockers receive α ∝ TAO share |
| **No lockups, no unlocks, instant TAO withdrawal** |
| Yield = (Validator α to pool) / (Total TAO locked) |

| **Revenue Buyback** |
|---------------------|
| 100% revenue → Market buy α (TWAP 24h) |
| 90% burn, 10% treasury replenish |
| Creates α/TAO floor + scarcity |

| **Why This Design** |
|---------------------|
| No investor unlocks → no overhang |
| Team paid only via emissions → zero dump risk |
| Immutable → no governance capture |
| Validator emissions → staker yield = **native dTAO mechanics** |

---

## 3. IMPLEMENTATION DECISIONS — YOUR CALL

### 3.1 JAX Ecosystem Choices

| Decision | Options | Your Rec? |
|----------|---------|-----------|
| **Neural Net Library** | Haiku / Flax / Equinox | |
| **Optimizers** | Optax (standard) / Custom | |
| **Distributed Training** | pjit / pmap / multi-host | |
| **Checkpointing** | Orbax / Custom | |

### 3.2 Phase 0 Backbones (Pick 3-4)

| Candidate | JAX Status | Physics Fit |
|-----------|------------|-------------|
| **FNO** | Ported / Native | Spectral, good for smooth |
| **GINO** | Ported / Native | Graph-based, handles irregular domains |
| **WNO** | Ported / Native | Wavelet, multi-scale |
| **Transolver** | Ported / Native | Attention-based, flexible |
| **DeepONet** | Need port | Classic, benchmark standard |

**Need decision**: Which 3 first? Existing JAX ports or port from PyTorch?

---

### 3.3 Physics Gate Implementation

| Gate | Implementation Approach | Questions |
|------|------------------------|-----------|
| **Mass Conservation** | Divergence operator (JAX grad) → L2 norm | Threshold from FEniCS validation? |
| **Energy Stability** | Time-derivative of energy functional | How to compute for each PDE? |
| **Boundary Satisfaction** | Mask + MSE on boundary points | Relative vs absolute tolerance? |
| **Rollout Stability** | 1000-step autoregressive + perturbation | Perturbation magnitude schedule? |
| **UQ Calibration** | Ensemble / Dropout / Conformal? | **Need method decision** |

**Calibration**: Per-physics-class thresholds from FEniCS validation data, or unified?

---

### 3.4 Landscape Agent — Highest Technical Risk

| Component | Options | Questions |
|-----------|---------|-----------|
| **PySR Integration** | Python call / Julia bridge / JAX-native symbolic? | Batch symbolic regression? |
| **Double ML** | EconML (Python) / Custom JAX implementation? | Sample efficiency for causal effects? |
| **ModelingToolkit.jl Bridge** | JuliaCall / JSON serialization / PyCall? | How to get structured losses into JAX training? |
| **Specialist Distillation** | Knowledge distillation loss / Architecture sharing? | What's the "specialist" unit? |

**Phasing**: PySR first (Phase 0) → Double ML (Phase 1) → Cross-domain causal (Phase 2)?

---

### 3.5 Validator Training Pipeline

| Decision | Options |
|----------|---------|
| **Single GPU first?** | Start single GPU, add multi-GPU Phase 1? |
| **Checkpointing** | Every N steps? On preemption? |
| **Preemption Handling** | Resume from checkpoint? Re-queue? |
| **Online Residual Monitoring** | JAX callback every N steps? Adaptive loss re-weighting bounds? |

---

### 3.6 MCP & Miner Toolkit

| Decision | Options |
|----------|---------|
| **MCP Server** | Python FastAPI (simpler) / Rust (perf) |
| **Agent SDK** | Python only / Python + TypeScript |
| **Estimation Mode** | Linear sensitivity / Small proxy model / Both? |
| **Noisy Prior Perturbation** | Gaussian noise on weights? Dropout? Config space noise? |

---

### 3.7 ONNX Export & Deployment

| Decision | Status |
|----------|--------|
| **jax2onnx Maturity** | Need test this week — custom ops for physics gates? |
| **TensorRT Optimization** | Post-export step? Dynamic shapes? |
| **Model Card Schema** | JSON with embedded ONNX? Separate artifact? |

---

### 3.8 Abaqus Ingestion (Phase 1)

| Approach | Options |
|----------|---------|
| **ODB → Training Data** | Python (abaqus2jax) / Julia (Ferrite.jl) / Custom |
| **Mesh + Fields** | Extract displacement/stress/strain → interpolate to regular grid? |
| **Scope** | Phase 1: mesh + primary fields only |

---

## 4. PHASE 0 SCOPE — 90 DAYS TO TESTNET

| Month | Focus | Key Deliverables |
|-------|-------|------------------|
| **1** | Foundation | Validator Docker, 7 PDE generators, Physics gates 1-3, Backbone registry (3), Training pipeline |
| **2** | Subnet Mechanics | MCP server, Miner Toolkit (Estimation + Light), Emission contracts, TAO-α pool, Model Card generator, ONNX export |
| **3** | Quality & Revenue Prep | Gate calibration, Generator audit package, Model Zoo API v1, Sponsored Challenge factory, Testnet 3 validators + 10 miners |

---

## 5. OPEN QUESTIONS / DISAGREEMENTS TO RESOLVE

| # | Topic | My Lean | Your View? |
|---|-------|---------|------------|
| 1 | JAX library (Haiku/Flax/Equinox) | Flax (ecosystem) | |
| 2 | Phase 0 backbones (3-4) | FNO, GINO, WNO | |
| 3 | Gate thresholds: per-class or unified? | Per-class (FEniCS calibrated) | |
| 4 | UQ Gate method | Conformal prediction (finite-sample) | |
| 5 | Landscape Agent: PySR + DML parallel or sequential? | Sequential (PySR Phase 0) | |
| 6 | ModelingToolkit.jl bridge | JSON serialization (simpler) | |
| 7 | Validator: single GPU start? | Yes (reduce Phase 0 complexity) | |
| 8 | MCP server language | Python FastAPI (velocity) | |
| 9 | Noisy prior perturbation method | Config-space Gaussian noise | |
| 10 | ChallengeWinnerTracker decay half-life | 30 days (tunable) | |

---

## 6. NEXT STEPS

| This Week | Owner |
|-----------|-------|
| JAX backbone audit — which 3, port status, training scripts | **You** |
| Generator implementation start (pair program) | **Both** |
| Gate calibration design — FEniCS validation cases per PDE | **You** |
| jax2onnx test with FNO + custom ops | **You** |
| Hiring: Infra Eng + Platform Eng specs | **Me** |

| Next Meeting | Focus |
|--------------|-------|
| Week 1 Friday | Decisions logged, blockers raised, generator progress |

---

**This is my first stab. Where is the design wrong? What did I oversimplify? What will bite us in implementation?**
