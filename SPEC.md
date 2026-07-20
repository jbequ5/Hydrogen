# SPEC.md — Carbon PDE Subnet Technical Specification (Buildable Level with Strategic Emphasis)

**Version:** 4.6 (Updated July 2026) — **Upgraded Validator & MCP Workflows**
**Audience**: Researchers and engineers with PhD-level background in Physics, Computational Mechanics, or Scientific Computing.

This specification provides sufficient detail for a domain expert to understand the scientific rationale, implementation logic, and expected behavior of every major component. It is intended to be buildable and scientifically defensible.

---

## 1. Scientific Motivation & Strategic Positioning

High-fidelity simulation remains the bottleneck in engineering design, optimization, digital twins, and real-time control. Traditional solvers scale poorly with design space size or real-time requirements. Pure data-driven ML surrogates are fast but frequently violate conservation laws, stability conditions, or boundary physics, rendering them unreliable for downstream engineering use.

The space for AI-powered physics simulation and Neural Operators is still **nascent**. There is a tremendous amount left to discover in *how* to best build, train, and use these models for real engineering problems.

Centralized teams explore this space linearly. Carbon is designed to explore it in parallel across thousands of strategies with strong selection pressure from hidden adversarial validation and compounding knowledge via the Landscape Agent.

**Core Thesis**: A properly aligned decentralized subnet can discover superior Neural Operator training methodologies faster and cheaper than centralized players, while providing trustless, verifiable robustness.

---

## 2. Validator Docker Image, Backbone Selection, Training, Evaluation & Advanced Features

### 2.1 Strategy JSON Schema (Input Contract)
Miners submit strategies as structured JSON. The validator must parse this to select backbone, configure training, data mixture, and evaluation behavior.

Key extensible fields include `backbone`, `training` (optimizer, lr_schedule, loss_weights, curriculum, data_mixture), `conditioning`, and `uncertainty`.

### 2.2 Backbone Registry & Dynamic Instantiation
The Docker image contains a Backbone Registry. Upon receiving JSON, the validator looks up the backbone type, instantiates it with provided config, applies conditioning/uncertainty modules, and seeds weights deterministically.

### 2.3 Data Pipeline & Deterministic Training
The validator builds a seeded data pipeline from the `data_mixture`:
- Procedural data generated on-the-fly via seeded generators.
- The Well slices sampled deterministically.
- Custom datasets (Phase 1+) loaded with seeded loaders.

Training executes with full hierarchical seeding for reproducibility. Loss formulation, curriculum, and optimizer follow the JSON exactly.

### 2.4 Held-Out Evaluation + Hidden Stress + Physics Gates
After training:
1. Evaluate on official held-out benchmark data.
2. Generate fresh `StressTestSet` (seeded).
3. Run model on all stress variants.
4. Apply hard/soft physics gates.
5. Compute final 45/30/25 score via HydrogenScorer.

Only strategies improving the current best combined score receive strong weight.

### 2.5 Multi-Fidelity Evaluation Pipeline (New — Phase 0+)
To improve throughput while preserving adversarial signal:
- **Tier 1 (Cheap)**: Low-fidelity stress (fewer variants, lower resolution or reduced rollout length). Quick filter.
- **Tier 2 (Full)**: Only strategies passing Tier 1 thresholds proceed to full hidden stress testing.

Thresholds and tier definitions are challenge-specific and versioned. This enables significantly more parallel strategy exploration without weakening the core adversarial mechanism.

### 2.6 Uncertainty-Aware Stress Prioritization (New — Phase 1+)
When the backbone supports uncertainty (evidential outputs or ensemble mode), the validator can prioritize or re-weight stress variants where epistemic uncertainty is high. This focuses adversarial pressure on the regions where the model is least confident, representing a more sophisticated form of robustness testing.

### 2.7 Online Physics Residual Monitoring + Adaptive Behavior (New — Phase 0+)
During training, the validator monitors PDE residuals and conservation metrics in real time. Configurable behaviors include:
- Dynamic loss weight adjustment (within JSON-defined bounds).
- Early stopping on persistent physics violations.
- Logging of residual trajectories for the Landscape Agent.

This makes training itself more physics-aware and supports discovery of robust training dynamics.

### 2.8 Automated Strategy Provenance & Model Card Generation (New — Phase 0+)
Every submission (test or production) automatically generates a structured **Model Card** containing:
- Exact strategy JSON and version.
- Backbone, hyperparameters, data mixture, loss weights, curriculum.
- Training curves (hashed).
- Held-out metrics.
- Stress test summary + gate violation details (with physics explanations where possible).
- Key symbolic features extracted.
- Uncertainty/robustness statistics.

These cards are logged, versioned, and fed to the Landscape Agent. They dramatically improve auditability and collective intelligence.

### 2.9 Docker Implementation
The image is self-contained with the full registry, data generators, stress system, scorer, reproducibility harness, and model card generator. Strategy JSON can be submitted via MCP or mounted volume. The container enforces determinism and produces reproducible artifacts.

---

## 3. Agent-Friendly MCP Mining Loop, Internal Testing & Advanced Features

### 3.1 Testing Philosophy
Even "test" runs should provide **real signal**. Therefore, test modes involve actual (light) training followed by gated evaluation under stress. This enables fast, meaningful iteration for both human miners and autonomous agents without compromising scientific integrity.

### 3.2 Testing Modes

**Mode A: Light Training + Gated Evaluation (Default Recommended Mode)**
- Reduced training budget (e.g. 25-40% epochs or accelerated curriculum).
- Same backbone, loss formulation, and data mixture as specified.
- After training: held-out evaluation + hidden stress testing (can use reduced variant set for speed) + **full physics gates**.
- Produces a real test score using the 45/30/25 formulation.
- Does **not** update the main leaderboard but is logged and can contribute (lower weight) to the Landscape Agent.

**Mode B: Simulated / Cached Approximation (Early Prototyping)**
- Uses fast approximations or cached training dynamics.
- Still applies stress testing and physics gates.
- Clearly labeled as simulated; given lower weight by the Landscape Agent.

**Mode C: Full Production Submission**
- Complete training + full hidden stress + gates.
- Only these can set new best combined scores and earn strong emissions weight.

### 3.3 Prior-Informed Warm Start from Landscape Agent (New — Phase 1+)
In test mode (and optionally production), agents can request initialization from the current best priors or distilled specialist weights for the challenge + backbone combination. This is retrieved from the Landscape Agent’s knowledge base.

This dramatically accelerates discovery and directly leverages the compounding intelligence of the subnet.

### 3.4 Explainable Failure Diagnostics (New — Phase 0+)
Test and production runs return rich, interpretable diagnostics in addition to scores:
- Locations and types of high residual or gate violations (e.g., "shock capturing failure in high-frequency region").
- Spectral or conservation drift analysis where applicable.
- Uncertainty hotspots (if uncertainty module is active).
- Comparison against recent successful strategies on similar challenges.

This greatly improves iteration speed for both human miners and autonomous agents.

### 3.5 Pareto / Multi-Objective Reporting in Test Mode (New — Phase 1+)
Light test mode can optionally return the Pareto front across physics fidelity, robustness, and accuracy instead of (or in addition to) a single scalar score. This helps agents discover interesting trade-off strategies and provides richer data to the Landscape Agent.

### 3.6 Defensibility & Anti-Gaming
- Clear separation: Test modes never affect official leaderboard or primary emissions.
- Rate limiting and credit system on test modes.
- All runs (test and production) are fully deterministic and reproducible.
- Full provenance and model card logging for every run.
- Phased difficulty in testing while still applying hard physics gates.
- Landscape Agent can use test data (with appropriate weighting) to improve priors.

### 3.7 Benefits for SOTA Innovation
This design strongly supports state-of-the-art strategy development:
- Autonomous agents can run closed-loop optimization (Bayesian, evolutionary, RL) using high-signal gated test feedback.
- Human miners can rapidly prototype novel ideas with meaningful physics-constrained feedback in minutes rather than hours.
- The combination of light-but-real training + adversarial gated evaluation creates an environment that rewards genuine methodological innovation.

### 3.8 MCP Implementation
MCP exposes endpoints for different modes with streaming support. Persistent sessions and hotkey-based authentication are supported, with optional higher quotas for high-performing or staked agents.

---

## 4. Challenges by Phase (Specific Problem Definitions)

### 4.1 Phase 0: Foundational Single-Physics Challenges

| ID | Problem | Dimension | Key Physics | Reference / Notes |
|----|---------|-----------|-------------|-------------------|
| 1 | Poisson | 2D/3D | Elliptic, source-driven | Standard benchmark; variable source amplitude/location, coefficient fields |
| 2 | Darcy | 2D/3D | Elliptic, heterogeneous media | Variable permeability fields (smooth + discontinuous); tests conservation & maximum principle |
| 3 | Burgers | 2D | Hyperbolic, nonlinear advection + viscosity | Shock formation/capturing, conservation, long-time stability |
| 4 | Navier-Stokes (laminar) | 2D/3D | Incompressible flow | Reynolds-number variation in laminar regime; divergence-free constraint, energy stability |
| 5 | Heat | 2D | Parabolic, transient conduction | Time-dependent forcing, variable conductivity, long-term decay |
| 6 | Linear Elasticity | 2D | Vector mechanics, equilibrium | Material property variation (Young's modulus, Poisson ratio), boundary displacement |
| 7 | Thermo-Elasticity | 2D | Coupled thermal-mechanical | Thermal expansion, coupling strength, temperature loading; tests coupled conservation |

Each challenge includes public training/holdout splits and hidden stress configurations. Symbolic metadata is attached.

### 4.2 Phase 1: Customization Layer
Same 7 challenges + custom datasets and LoRA/custom strategy support.

### 4.3 Phase 2: Verified Multi-Physics Composition
FSI (Turek/Hron), CHT, and expanded Thermo-Elasticity with preCICE and reference solutions.

### 4.4 Phase 3: 3D Multi-Physics & Advanced Composition
3D FSI/CHT/Thermo-elasticity with turbulence, 3D-specific gates, and curriculum from 2D specialists.

---

## 5. Validation Strategy — Scientific Rigor & Competitive Edge

Multi-objective scoring (45/30/25), hard/soft physics gates, and hidden stress testing as previously defined. Multi-fidelity and uncertainty-aware extensions (Sections 2.5–2.6) enhance throughput and sophistication without weakening adversarial guarantees.

---

## 6. Determinism & Reproducibility
Hierarchical seeding, framework controls, and Docker-based reproducibility harness ensure all training, stress testing, and scoring (including multi-fidelity tiers) are reproducible and auditable.

---

## 7. Landscape Agent — Symbolic & Causal Compounding
Ingests results, model cards, and diagnostics from both production and high-quality test runs. Extracts symbolic features and applies Double Machine Learning for causal insights into effective training methodologies. Updates priors and drives specialist distillation.

Prior-informed warm starts and model card data directly enhance the Landscape Agent’s effectiveness.

---

## 8. Detailed Implementation Components
- Stress Generators & StressEvaluator (with multi-fidelity support)
- HydrogenScorer
- Backbone Registry (dynamic instantiation from JSON)
- Validator Docker image (with model card generator, residual monitoring, uncertainty handling)
- MCP layer (multi-mode testing with light training + gated evaluation, explainable diagnostics, prior warm-start support)
- generate_challenge()
- Reproducibility Harness

---

## 9. Phased Roadmap (Build-Level)

**Phase 0**:
- Core stress generators, evaluator, scorer, determinism, MCP basic testing (light training + gated evaluation)
- Backbone registry + JSON parsing + training pipeline in Docker
- Automated model card / provenance generation
- Explainable diagnostics in test mode
- Multi-fidelity evaluation pipeline (Tier 1 cheap filter + Tier 2 full)
- Online residual monitoring + basic adaptive behavior

**Phase 1**:
- Prior-informed warm start from Landscape Agent
- Uncertainty-aware stress prioritization
- Pareto / multi-objective test reporting
- Enhanced MCP testing modes and credit system
- LoRA/custom backbone support

**Phase 2+**: preCICE multi-physics, 3D support, advanced agent features (trajectory memory, agent-proposed stress variants).

---

## 10. Scientific Defensibility & Competitive Differentiation
Every extension (multi-fidelity, uncertainty-aware stress, residual monitoring, model cards, explainable diagnostics, prior warm starts) is designed to be scientifically grounded, reproducible, and auditable. These features strengthen Carbon’s position as the decentralized discovery and robustness engine for Software Defined Machines and Living Digital Twins, enabling faster innovation in Neural Operator methodologies than centralized platforms can achieve.

---

*This specification is written to be scientifically rigorous and buildable. Reference the implementation in `neurons/` and supporting design documents for concrete code.*
