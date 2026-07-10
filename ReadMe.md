# Hydrogen: The Self-Improving Physics Engine

*A Bittensor subnet turning the sim-to-real gap into a compounding knowledge economy.*

---

## The Blade That Melted

2019. A major aerospace company. Six months training a neural operator to predict thermal stress in turbine blades. Two percent test error. Three weeks in production, a blade melted in testing.

The surrogate hadn't learned physics. It had learned to minimize MSE. Energy conservation drifted 0.3% in a regime they hadn't tested. In the real world, 0.3% energy drift means a blade melts.

This isn't isolated. A fusion lab's neural operator predicted plasma stability perfectly—until it didn't. A semiconductor firm's layout optimizer passed every regression test—until a new geometry violated divergence-free. The sim-to-real gap isn't an accuracy problem.

**It's a trust problem.**

---

## The Technology That Almost Changed Everything

Neural operators (FNO, PINO, DeepONet, GNO, OFormer) are the most important breakthrough in computational science in two decades.

Traditional simulation discretizes physics onto meshes and solves linear systems—O(N³) scaling. For 3D turbulence at real Reynolds numbers, you need exascale machines and weeks of compute.

Neural operators learn the **solution operator itself**: the mapping from forcing, initial conditions, material properties → solution field. Inference is a forward pass. Milliseconds on a GPU. Cost amortized over infinite queries.

The real breakthrough: **discretization invariance**. Following the Berner et al. recipe, a properly constructed neural operator learns a mapping between *function spaces*, not vectors. Train on 64², evaluate on 256²—it works because the architecture respects the continuous operators underneath. This enables zero-shot super-resolution, multi-scale modeling, geometry transfer.

The theory is solid (Berner et al., Nature 2026). The implementations are production-ready (PhysicsNeMo, NeuralOperator). But they have a fatal flaw: **they optimize for loss functions, not physics.**

A surrogate trained on MSE minimizes MSE. It doesn't know ∇·u = 0 is a law, not a suggestion. It doesn't know energy dissipation is a constraint, not a penalty. It doesn't know shocks must satisfy Rankine-Hugoniot. And because training distributions never cover deployment space, violations appear exactly where they hurt most: the extrapolation regime, the edge case, the novel design.

---

## Starting on Solid Ground

We are not building neural operators from scratch. We are building on two mature, production-grade foundations:

**PhysicsNeMo** (NVIDIA) provides the reference implementations: FNO, PINO, DeepONet, GNO, OFormer with built-in physics-informed losses, conservation constraints, spectral layers, boundary handling, and UQ tooling. It is the PyTorch of physics-informed neural operators—battle-tested in industrial deployments from climate modeling to semiconductor design.

**NeuralOperator** (the library behind the Berner et al. Nature paper) provides the mathematical backbone: the layer conversions that make standard architectures discretization-agnostic, the quadrature weights that preserve conservation, the spectral and graph operator implementations. It is the reference implementation of the theory.

Hydrogen wraps these libraries in pinned, versioned Docker images. Validators pull `hydrogen/validator:pino-v24.09` and get exactly the same PhysicsNeMo + NeuralOperator + PyTorch + CUDA stack every time. Miners never install dependencies. They only tune the knobs these libraries already expose.

We are not inventing the engine. We are building the **race track, the timing system, and the engineering team that learns from every lap.**

---

## The Mechanism

**Open challenges.** At any time, a set of challenges is open for competition. Each challenge defines a PDE problem—Poisson, Darcy, Burgers, Navier-Stokes, Heat, Elasticity, Thermo-elasticity—in 2D or 3D, with a public training split, a public holdout set, and a **hidden stress test** generated procedurally from the challenge ID (shifted Reynolds numbers, resolutions, geometries, forcing). No miner has ever seen the stress test.

**Miners submit strategy JSONs.** A strategy specifies: backbone choice (FNO, PINO, DeepONet, GNO, OFormer), a **loss vector** with per-physics-term weights (pde_residual, conservation, boundary, symmetry, coupling), optimizer, curriculum schedule, UQ method (deep ensemble, conformal, evidential). They pay 0.1 TAO. They never touch a GPU. They never upload weights.

**Validators run the training.** They pull the pinned backbone image, inject the miner's JSON, train on the public training split, evaluate on the public holdout, then run the hidden stress test through **hard physics gates**:
- Mass conservation: ‖∇·u‖₁ < 1e-3
- Energy dissipation: dE/dt ≤ 1e-4
- Boundary satisfaction
- Rollout stability over 100 steps
- UQ calibration: 90% prediction intervals must cover truth 90% of the time (±2%)

Hard failure = score zero. No bonuses. No partial credit. Physics is binary.

**Score = log(E_baseline) - log(E_submission).** Improvement measured in log-space against the current baseline. Median of five validators determines the winner. Winner takes the 41% emission share.

**Every submission becomes a StrategyFragment.** The config, the score, the stress result, UQ metrics, and its lineage in the fragment DAG. Winning or losing—every fragment teaches the Landscape.

---

## The Landscape Agent

The Landscape doesn't just correlate. It runs **Double Machine Learning on the fragment DAG** to estimate `P(improvement | do(param))`—the *causal effect* of a config change, not the spurious correlation.

It discovers that Fourier modes 32 help *only when* physics loss > 1.0. That curriculum helps *only when* start resolution ≤ 0.5× end resolution. That ghost cells prevent boundary locking *only for* elasticity and NS, not Poisson.

Every challenge cycle, it proposes a new baseline JSON incorporating the strongest causal effects. Every distillation cycle, it takes the top-K strategies and distills them into **ONNX specialists** via multi-teacher distillation—regression tested against the same stress tests—and publishes them to the Specialist Bank with validity domains and dual licensing (AGPL-3.0 + commercial).

The Landscape is funded by the Owner's 18% emissions plus a time-locked treasury (10% of Owner emissions, 6-month cliff, 2-year vest, 3/5 multi-sig). The agent is replaceable; the causal knowledge graph is not.

---

## Phases

**Phase 0: The Causal Baseline.** Strategy JSONs for 10 problems spanning the PDE taxonomy: Poisson 2D/3D (elliptic constant-coeff), Darcy 2D/3D (elliptic variable-coeff), Burgers (nonlinear advection/shocks), Navier-Stokes 2D/3D (incompressible flow, turbulence gateway), Heat with variable diffusivity (transient diffusion), Elasticity (vector output, tensor physics), Thermo-elasticity (multi-physics coupling with loss_vector). All have public train/holdout + hidden stress tests + PhysicsNeMo reference implementations. Landscape builds causal fragment DAG, proposes baseline updates. 3D problems run on 24GB GPUs with gradient checkpointing.

**Phase 1: Adapters & Data Markets.** Miners submit LoRA adapters (tiny weight deltas) and custom datasets (high-fidelity DNS, curated permeability fields). Landscape pays data royalties for measured impact. First ONNX specialists distilled, dual-licensed (AGPL-3.0 + commercial).

**Phase 2: Specialist Marketplace.** Miners select specialists by ID—zero training, instant inference. Specialist Bank becomes composable library. Multi-teacher distillation across the bank produces Foundation Operator v1. Commercial fine-tuning API launches (encrypted client data → TEE adaptation).

**Phase 3+: Foundation Operator.** Foundation Operator becomes core IP—one model conditioned on ProblemSignature, fine-tunable in minutes. SAGE agent proposes new architectures, loss terms, data bounties. Custom surrogate service: client submits encrypted geometry → verified, calibrated, physics-compliant specialist in minutes.

---

## Design Choices

| We Chose... | Because... |
|-------------|------------|
| **Miners submit JSON strategies, not models** | Accessibility (laptop-only), verifiability (same code/data/seed), knowledge extraction (config = transferable insight), anti-gaming (no weight hiding) |
| **Validators run pinned Docker images** | Determinism, PhysicsNeMo integration, predictable cost, upgradability |
| **Procedural hidden stress tests + hard physics gates** | Static holdouts get overfit. Physics violations are binary—dangerous, not "99% correct." |
| **Loss vector, not scalar** | Multi-physics needs per-term balance. Miners learn scaling laws. |
| **Causal inference (DML) > correlation** | "Fourier modes help" only when physics loss > 1.0. DML estimates `P(improvement | do(param))` on the fragment DAG. |
| **10 problems spanning the PDE taxonomy** | Cross-cutting principles only learnable with full coverage. |
| **3D Navier-Stokes in Phase 0** | Highest-value surrogate class. 24GB GPUs are commodity; Landscape needs 3D scaling laws now. |
| **Owner-funded Landscape + time-locked treasury** | Owner revenue comes from Landscape value, not skimming miners. Resilience guaranteed. |

---

## Staged Business Plan & Moat

**The Asset:** The Landscape's causal knowledge graph—causally-validated interventions across 10 PDE families, growing every challenge cycle. This dataset does not exist anywhere. NVIDIA, ANSYS, Siemens pay seven figures for "training best practices" data.

**The Moat:** Structural, not technical. Benchmarks are public. Backbones are PhysicsNeMo. The *causally-validated intervention effects* require the subnet's three-legged flywheel: miners explore for emissions, validators verify with physics gates for emissions, Landscape distills causal knowledge for Owner revenue.

**Staged Revenue:**
- **Phase 0-1:** TAO emissions fund operations. Landscape builds asset.
- **Phase 1-2:** Specialist licensing (AGPL-3.0 ecosystem + commercial dual-license). Data royalties from custom datasets.
- **Phase 2-3:** Foundation Operator API (fine-tuning on encrypted client data in TEE). Custom surrogate service (encrypted geometry → verified specialist).
- **Phase 3+:** Revenue > emissions. Emissions become "innovation bonus." Physics infrastructure layer.

**Downside Protection:** TAO crash → validator costs covered by 0.1 TAO fee (scales); Owner treasury time-locked (6-month cliff, 2-year vest, 3/5 multi-sig). Miner exodus → fragments → specialists → Foundation Operator survives. Physics checks too hard → soft penalties + diagnostics keep miners iterating.

---

## Implications & Vision

**For Computational Science:** The first continuous, adversarial, physics-gated benchmark in history. Tribal knowledge becomes public, versioned, auditable, *causal*. The sim-to-real gap becomes a measured, shrinking, attributable quantity.

**For Engineering Practice:** Custom surrogates on demand. "I need a surrogate for my heat exchanger geometry." → Submit encrypted geometry → Get back an ONNX specialist fine-tuned in minutes → Runs on laptop → Conserves energy by construction → Calibrated uncertainty intervals. A startup gets Boeing-grade surrogate without HPC. 72-hour CFD → 10-millisecond inference. Design loops from months to hours.

**For AI in Science:** Proof that causal inference works at scale (largest deployed causal ML in science). Proof that incentive-aligned decentralization beats centralization. A template for protein folding, materials discovery, drug design, climate modeling.

**For Bittensor:** A subnet where emissions buy verified physics improvements with causal proof. A template for "knowledge-compounding" subnets. Proof that subnets can build IP assets, not just burn emissions.

*Hydrogen: Where every training run teaches the network. Where physics is the only metric that pays. Where the sim-to-real gap becomes a shrinking, measured, attributable quantity.*
