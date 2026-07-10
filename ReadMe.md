# Hydrogen: The Self-Improving Physics Engine

*A Bittensor subnet for Physical Intelligence.*

## The Current State of Physics ML

Neural operators (FNO, PINO, DeepONet, GNO, OFormer) are the most important breakthrough in computational science in two decades.

Traditional simulation discretizes physics onto meshes and solves linear systems—O(N³) scaling. For 3D turbulence at real Reynolds numbers, you need massive machines and weeks of compute.

Neural operators learn the **solution operator itself**: the mapping from forcing, initial conditions, material properties → solution field. Inference is a forward pass. Milliseconds on a GPU. Cost amortized over infinite queries.

The real breakthrough: **discretization invariance**. Following the Berner et al. recipe, a properly constructed neural operator learns a mapping between *function spaces*, not vectors. Train on 64², evaluate on 256²—it works because the architecture respects the continuous operators underneath. This enables zero-shot super-resolution, multi-scale modeling, geometry transfer.

The theory is solid (Berner et al., Nature 2026). The implementations are production-ready (PhysicsNeMo, NeuralOperator). But they have a fatal flaw: **they optimize for loss functions, not physics.**

A surrogate trained on MSE minimizes MSE. It doesn't know ∇·u = 0 is a law, not a suggestion. It doesn't know energy dissipation is a constraint, not a penalty. It doesn't know shocks must satisfy Rankine-Hugoniot. And because training distributions never cover deployment space, violations appear exactly where they hurt most: the extrapolation regime, the edge case, the novel design.

---

## The Current Tribal Knowledge Trap

The field knows this. Every paper proposes a new physics-informed loss, a new architecture tweak, a new training trick.

But discoveries stay tribal.

The PhD who discovers that *curriculum learning + ghost-cell boundaries + physics loss weight 1.8* works for transonic flow publishes a paper. Two years later, a team at another institution rediscovers it. Another PhD finds that Fourier modes scale with dimension as N^(d/2). Another learns that curriculum learning only helps when start resolution ≤ 0.5× end resolution.

**The field moves at publication speed, not discovery speed.**

We don't need better neural operators. We need a system that **compounds knowledge about how to train them.**

---

## The Foundation

We are not building neural operators from scratch. We are building on two mature, production-grade foundations:

**PhysicsNeMo** (NVIDIA) provides the reference implementations: FNO, PINO, DeepONet, GNO, OFormer with built-in physics-informed losses, conservation constraints, spectral layers, boundary handling, and UQ tooling. It is the PyTorch of physics-informed neural operators—battle-tested in industrial deployments from climate modeling to semiconductor design.

**NeuralOperator** (the library behind the Berner et al. Nature paper) provides the mathematical backbone: the layer conversions that make standard architectures discretization-agnostic, the quadrature weights that preserve conservation, the spectral and graph operator implementations. It is the reference implementation of the theory.

Hydrogen wraps these libraries in pinned, versioned Docker images. Validators pull `hydrogen/validator:pino-v24.09` and get exactly the same PhysicsNeMo + NeuralOperator + PyTorch + CUDA stack every time. Miners never install dependencies. They only tune the knobs these libraries already expose.

We are not inventing the engine. We are building the **race track, the timing system, and the engineering team that learns from every lap.**

---

## Why Bittensor? Why a Subnet?

Because the incentive structure *is* the product.

In a centralized benchmark, you optimize for the metric. In a subnet, you optimize for *what validators actually check*—and validators check physics. The hidden stress test is the ultimate anti-gaming mechanism: you cannot overfit what you've never seen. Physics gates (mass conservation, energy dissipation, rollout stability, UQ calibration) are binary—you pass or you fail. No "good enough for the leaderboard."

Because the barrier to entry must be an idea, not a GPU cluster. A researcher in Bangalore with a clever curriculum idea competes on equal footing with a quant fund running H100s. The H100s run the validation; the clever idea wins the emissions.

Because validator consensus replaces trust. Physics checks are deterministic. The same backbone image, same data, same miner config run by five validators produces five identical scores. Median consensus. No politics.

Because knowledge must compound autonomously. In traditional science, a failed experiment teaches nobody. In Hydrogen, a losing strategy teaches the Landscape "don't do that for this PDE class." The 99% of submissions that don't win become the training data for the next baseline.

Bittensor provides the economic substrate where **verified improvement is the only currency**, infrastructure is paid for by the value it creates, and the moat compounds automatically.

---

## The Mechanism

**Open challenges.** A set of challenges is open for competition at any time. Each challenge defines a PDE problem with a public training split, a public holdout set, and a **hidden stress test** generated procedurally from the challenge ID (shifted Reynolds numbers, resolutions, geometries, forcing). No miner has ever seen the stress test.

**Miners submit strategy JSONs.** A strategy specifies: backbone choice (FNO, PINO, DeepONet, GNO, OFormer), a **loss vector** with per-physics-term weights (pde_residual, conservation, boundary, symmetry, coupling), optimizer, curriculum schedule, UQ method (deep ensemble, conformal, evidential). They pay 0.1 TAO submission fee. They never touch a GPU. They never upload weights.

**Validators run the training.** They pull a pinned Docker image (PhysicsNeMo + NeuralOperator, pinned PyTorch/CUDA), inject the JSON, train on the public training split, evaluate on the public holdout, then run the hidden stress test through **hard physics gates**:
- Mass conservation: ‖∇·u‖₁ < 1e-3
- Energy dissipation: dE/dt ≤ 1e-4
- Boundary satisfaction
- Rollout stability over 100 steps
- UQ calibration: 90% prediction intervals must cover truth 90% of the time (±2%)

Hard failure = score zero. Physics is binary.

**Score = log(E_baseline) - log(E_submission).** Improvement measured in log-space against the current baseline. Median of five validators determines the ranking.

**Emission distribution per challenge.** Each challenge has an emission budget = total subnet emission / number of active challenges. The top 4 ranked miners split that challenge's emission budget: **40% / 30% / 20% / 10%**. Winner takes 40%, 2nd takes 30%, 3rd takes 20%, 4th takes 10%. Ranks 5+ receive zero emissions for that challenge.

**Every submission becomes a StrategyFragment.** The config, the score, the stress result, UQ metrics, and its lineage in the fragment DAG. Winning or losing—every fragment teaches the Landscape.

---

## The Landscape Agent: Where the Magic Compounds

The Landscape doesn't just correlate. It runs **Double Machine Learning on the fragment DAG** to estimate `P(improvement | do(param))`—the *causal effect* of a config change, not the spurious correlation.

It discovers that Fourier modes 32 help *only when* physics loss > 1.0. That curriculum helps *only when* start resolution ≤ 0.5× end resolution. That ghost cells prevent boundary locking *only for* elasticity and NS, not Poisson.

Every challenge cycle, it proposes a new baseline JSON incorporating the strongest causal effects. Every distillation cycle, it takes the top-K strategies and distills them into **ONNX specialists** via multi-teacher distillation—regression tested against the same stress tests—and publishes them to the Specialist Bank with validity domains and dual licensing (AGPL-3.0 + commercial).

The Landscape is funded by the Owner's 18% emissions plus a time-locked treasury (10% of Owner emissions, 6-month cliff, 2-year vest, 3/5 multi-sig). The agent is replaceable; the causal knowledge graph is not.

---

## Phases: What Happens, Products, Revenue, TAM

### Phase 0: The Causal Baseline (Launch → Month 3)

**Challenges:** 10 single-physics PDEs.

| Problem | Dimension | Physics Class | Reference |
|---------|-----------|---------------|-----------|
| Poisson | 2D / 3D | Elliptic, constant-coeff | PhysicsNeMo |
| Darcy | 2D / 3D | Elliptic, variable-coeff | PhysicsNeMo / PDEBench |
| Burgers | 2D | Nonlinear advection/shocks | PhysicsNeMo |
| Navier-Stokes | 2D / 3D | Incompressible (2D vortex / 3D laminar Re≤100) | PhysicsNeMo / JHTDB |
| Heat | 2D | Transient, variable κ | PhysicsNeMo |
| Elasticity | 2D | Vector, tensor physics | PhysicsNeMo |
| Thermo-elasticity | 2D | Multi-physics, loss_vector | Generated (48 Tier 1) |

Each challenge provides: public training split, public holdout set, hidden stress test (procedural parameter/geometry shifts).

**What Happens:**
- Miners submit strategy JSONs daily; validators train, evaluate, stress-test
- Landscape ingests every StrategyFragment, runs DML causal inference on the fragment DAG
- Daily: Landscape proposes updated baseline JSON incorporating strongest causal effects
- Weekly: Landscape distills top-K strategies into ONNX specialists (regression-tested)

**Product:** Causal Knowledge Graph — 500+ causally-validated interventions across 10 PDE problems. Daily baseline updates incorporating causal effects.

**Technical Milestone:** Baseline log-improvement > 0.02/challenge averaged over 30 challenges. 500+ StrategyFragments in DAG. 5+ validators operational.

**Revenue:** $2-5M/yr licensing causal knowledge graph to NVIDIA/ANSYS/Siemens for "training best practices" datasets.

---

### Phase 1: Specialist Bank & Data Markets (Months 3-6)

**Challenges:** Same 10 problems. Miners now add LoRA adapters and custom datasets.

**What Happens:**
- Miners submit LoRA adapters (rank-4-8) and custom datasets (DNS data, curated permeability fields)
- Validators apply adapters, cache custom data, measure data impact
- Landscape pays **data royalties** (5% of emissions) for measured impact of custom datasets
- Weekly distillation: top-K strategies → ONNX specialists via multi-teacher distillation → regression-tested against same stress tests → published to Specialist Bank
- Specialists tagged with validity domains, dual-licensed (AGPL-3.0 + commercial)

**Product:** 20-30 verified ONNX specialists (Poisson, Darcy, NS-2D, Burgers, Heat, Elasticity) with validity domains, calibrated UQ, dual licensing (AGPL-3.0 + commercial). LoRA adapter support. Data royalty pipeline paying miners for custom datasets that measurably improve specialists.

**Technical Milestone:** ≥20 specialists in bank. Data royalties >5% emissions. Specialist reuse rate >80%.

**Revenue:** $10-50M/yr specialist licensing (AGPL-3.0 ecosystem + commercial dual-license), data royalties, fine-tuning API on encrypted client data (TEE).

---

### Phase 2: Composition Engine & Specialist Marketplace (Months 6-18)

**Challenges:** Multi-physics problems on **verified benchmarks first** (zero new data generation for Phase 2A).

**Phase 2A (Months 1-3):** Verified Benchmarks Only
| Challenge | Source | Physics | Specialist Pair |
|-----------|--------|---------|-----------------|
| FSI 2D-1/2/3 | Turek/Hron | Fluid-Structure Interaction | `ns_2d` + `elasticity_2d` + `fsi_coupling` |
| CHT: Solid cooling / Electronics | PDEBench | Conjugate Heat Transfer | `ns_2d` + `heat_2d` + `cht_coupling` |

**Phase 2B (Month 3):** Thermo-Elasticity. Only new data generation needed. Generate 48 Tier-1 references (β×κ×geometry) at 256² with FEniCS monolithic, mesh-converged. Cost: ~$3K.

**Phase 2C (Months 4-5):** Variant expansion (new Re, geometries, coupling strengths) on FSI/CHT/thermo-elasticity using existing references.

**What Happens:**
- Miners submit **specialist pipelines** — composing verified specialists with lightweight adapters for specific multi-physics problems. This is the **customizable surrogate product**.
- Landscape pays data royalties for custom datasets. Multi-teacher distillation produces new specialists.
- **Three-track leaderboard** on every multi-physics challenge:

| Track | Submission Format | What It Proves |
|-------|-------------------|----------------|
| **Monolith** | Single strategy JSON (end-to-end training config for coupled problem) | Can a monolithic model beat composition? |
| **Composition** | Specialist pipeline: `{"specialist_pipeline": [{"specialist_id": "ns_2d_v4"}, {"specialist_id": "heat_2d_v3"}, {"adapter_id": "cht_coupling_v2"}]}` | Does composition of specialists beat monolith? |
| **Specialist-Only** | Single specialist ID (no adapter) | How much does the coupling adapter matter? |

**Same hidden stress test, same physics gates, three parallel leaderboards.** 

**Phase 2C Exit Criteria (Go/No-Go for 3D):**
| Metric | Target | If Missed |
|--------|--------|-----------|
| Composition win rate | >60% (Composition > Monolith) | Pivot: deepen single-physics specialist depth |
| Specialist reuse | >80% compositions use ≥1 Bank specialist | Extend Phase 1 |
| Adapter innovation | >30% novel adapters | Expand adapter design space |
| Stress test pass rate | >70% compositions pass | Coupling brittle → simplify adapter design |

**Products:** 
Proven multi-physics strategy (FSI, CHT, thermo-elasticity). 
Specialist Bank (50+ specialists) composable via adapters: `elasticity_v3 + heat_v2 + thermal_expansion_adapter = thermo-elastic solver`. 
**Miners build customizable surrogates by composing specialists with adapters.**

**Technical Milestone:** Composition win rate >60% on FSI/CHT/thermo-elasticity. ≥50 specialists in bank. Specialist reuse >80%. Adapter innovation >30%.

**Revenue:** $50-200M/yr composition engine licensing (COMSOL, Ansys, Siemens), custom multi-physics pipelines ($10M-100M contracts), specialist marketplace fees.

---

### Phase 3: 3D Transition & Foundation Operator (Months 18+)

**Challenges:** 3D multi-physics (FSI, Thermo-elasticity, CHT) — same three-track leaderboard, same stress tests.

#### Phase 3.0 — 3D Single-Physics Foundations (Prerequisite)
3D Poisson, Darcy, NS-laminar, Heat, Elasticity specialists via curriculum distillation from 2D (zero-pad Fourier + noise → curriculum fine-tune → stress test validation). **Prerequisite for all 3D multi-physics.**

#### Phase 3.1 — 3D Turbulence Bridge (Critical Phase)
Dedicated 3-month phase to learn 3D turbulence from scratch (Re=50→500 curriculum, proper 3D spectral initialization, `ns_3d_turbulent_v1` with verified k^(-5/3) spectrum, 3D-specific stress gates: energy spectrum, Q-criterion, wall shear, Nu distribution). **Gate for all 3D multi-physics.**

#### Phase 3.2 — 3D Multi-Physics Rollout
| Phase | Challenges | Specialist Composition | Reference |
|-------|------------|------------------------|-----------|
| **3.2A** 3D FSI | Cylinder, flap, turbulent | `ns_3d_turbulent` + `elasticity_3d` + `fsi_3d_adapter` | preCICE partitioned |
| **3.2B** 3D Thermo-Elasticity | Bimetal, engine block, turbine blade | `elasticity_3d` + `heat_3d` + `thermal_expansion_3d` | FEniCS monolithic |
| **3.2C** 3D CHT | Electronics, turbine, battery | `ns_3d_turbulent` + `heat_3d` + `cht_3d_adapter` | OpenFOAM/COMSOL |

Same three-track leaderboard, same stress tests.

#### Phase 3.3 — Foundation Operator (LPM) **Product**
**Product:** A single unified neural operator conditioned on ProblemSignature that solves any PDE in the taxonomy. Fine-tunable on encrypted client data in minutes (TEE). Commercial fine-tuning API.

- **Multi-teacher distillation** across entire Specialist Bank (2D + 3D)
- **Conditioning:** ProblemSignature → FiLM layers modulate backbone
- **UQ Head:** Evidential (μ, σ, ν, α for Student-t)
- **Commercial API:** Client submits encrypted geometry/data → TEE fine-tuning (10-50 steps) → verified, calibrated, physics-compliant ONNX specialist returned in minutes

**Revenue:** $1B+ TAM. Foundation Operator API ($500-5K/model), custom surrogates ($50K-500K/yr), enterprise physics infrastructure layer.

---

## If This Works: The Implications

**For Computational Science:** The first continuous, adversarial, physics-gated benchmark in history. Tribal knowledge becomes public, versioned, auditable, *causal*. The sim-to-real gap becomes a measured, shrinking, attributable quantity.

**For Engineering Practice:** Custom surrogates on demand. "I need a surrogate for my heat exchanger geometry." → Submit encrypted geometry → Get back an ONNX specialist fine-tuned in minutes → Runs on laptop → Conserves energy by construction → Calibrated uncertainty intervals. A startup gets Boeing-grade surrogate without HPC. 72-hour CFD → 10-millisecond inference. Design loops from months to hours.

**For AI in Science:** Proof that causal inference works at scale (largest deployed causal ML in science). Proof that incentive-aligned decentralization beats centralization. A template for protein folding, materials discovery, drug design, climate modeling.

**For Bittensor:** A subnet where emissions buy verified physics improvements with causal proof. A template for "knowledge-compounding" subnets. Proof that subnets can build IP assets, not just burn emissions.

---

## The Honest Summary

| Phase | Business Status | Technical Risk | Revenue Independence |
|-------|-----------------|----------------|----------------------|
| **Phase 0** | Proven flywheel, sellable asset | Low | ✅ Yes |
| **Phase 1** | Specialist marketplace, recurring revenue | Low | ✅ Yes |
| **Phase 2** | Composition engine, high-value IP | Medium | ✅ Yes (2D multi-physics) |
| **Phase 3** | Moonshot (LPM) | **High (3D turbulence)** | ❌ Depends on 3D turbulence |

**The business is real at Phase 1. Profitable at Phase 2. Phase 3 is the 100x lottery ticket.**

*Hydrogen: Where every training run teaches the network. Where physics is the only metric that pays. Where the sim-to-real gap becomes a shrinking, measured, attributable quantity.*
