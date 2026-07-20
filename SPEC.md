# SPEC.md — Carbon PDE Subnet Technical Specification (Buildable Level with Strategic Emphasis)

This specification provides sufficient detail for a domain expert to understand the scientific rationale, implementation logic, and expected behavior of every major component. It is intended to be buildable and scientifically defensible.

---

## 1. Scientific Motivation & Strategic Positioning

High-fidelity simulation remains the bottleneck in engineering design, optimization, digital twins, and real-time control. Traditional solvers scale poorly with design space size or real-time requirements. Pure data-driven ML surrogates are fast but frequently violate conservation laws, stability conditions, or boundary physics, rendering them unreliable for downstream engineering use.

The space for AI-powered physics simulation and Neural Operators is still **nascent**. There is a tremendous amount left to discover in *how* to best build, train, and use these models for real engineering problems (loss formulations, curricula, conditioning, robustness under distribution shift, multi-physics coupling, long-horizon stability, etc.).

Centralized teams explore this space linearly and with limited internal testing. Carbon is designed to explore it in parallel across thousands of strategies with strong selection pressure from hidden adversarial validation.

**Core Thesis**: A properly aligned decentralized subnet can discover superior Neural Operator training methodologies faster and cheaper than centralized players, while gaining significant credibility through trustless, verifiable stress testing.

Carbon addresses this by creating a **decentralized, adversarially validated, self-improving engine** for physics-informed neural operator strategies. Key scientific and strategic advantages:

- Adversarial hidden stress testing forces robustness beyond public benchmarks.
- Hard physics gates enforce non-negotiable physical constraints.
- The Landscape Agent extracts symbolic structure and causal relationships, enabling compounding knowledge.
- Determinism and auditability ensure scientific reproducibility and trust.
- Decentralized parallel exploration replaces centralized linear search.

The system is designed so that a domain expert can verify that submitted strategies are not merely fitting data but are learning physically meaningful operators.

---

## 2. Challenges by Phase (Specific Problem Definitions)

### Phase 0: Foundational Single-Physics Challenges

| ID | Problem | Dimension | Key Physics | Reference / Notes |
|----|---------|-----------|-------------|-------------------|
| 1 | Poisson | 2D/3D | Elliptic, source-driven | Standard benchmark; variable source amplitude/location, coefficient fields |
| 2 | Darcy | 2D/3D | Elliptic, heterogeneous media | Variable permeability fields (smooth + discontinuous); tests conservation & maximum principle |
| 3 | Burgers | 2D | Hyperbolic, nonlinear advection + viscosity | Shock formation/capturing, conservation, long-time stability |
| 4 | Navier-Stokes (laminar) | 2D/3D | Incompressible flow | Reynolds-number variation in laminar regime; divergence-free constraint, energy stability |
| 5 | Heat | 2D | Parabolic, transient conduction | Time-dependent forcing, variable conductivity, long-term decay |
| 6 | Linear Elasticity | 2D | Vector mechanics, equilibrium | Material property variation (Young's modulus, Poisson ratio), boundary displacement |
| 7 | Thermo-Elasticity | 2D | Coupled thermal-mechanical | Thermal expansion, coupling strength, temperature loading; tests coupled conservation |

Each challenge includes public training/holdout splits and hidden stress configurations. Symbolic metadata (conservation laws, symmetries, boundary types) is attached.

### Phase 1: Customization Layer

Same 7 challenges + support for custom datasets (Abaqus ODB/.fil ingestion) and LoRA/custom strategy parameters. Focus remains on single-physics robustness with richer data diversity.

### Phase 2: Verified Multi-Physics Composition

**Phase 2A — Benchmark Problems**:
- FSI (Fluid-Structure Interaction): Turek/Hron 2D benchmarks (FSI-1/2/3). Reference: partitioned coupling via preCICE + OpenFOAM/CalculiX or equivalent. Key physics: fluid-structure interaction, added mass, vortex shedding.
- Conjugate Heat Transfer (CHT): Solid-fluid thermal coupling (electronics cooling, heat exchangers). Reference solutions from PDEBench/OpenFOAM.

**Phase 2B — Thermo-Elasticity Reference Suite**:
Generate ~48 mesh-converged Tier-1 reference cases at 256^{2} using FEniCS monolithic solver, varying thermal expansion coefficient (β), conductivity (κ), and geometry. Cost target: moderate compute for ground truth.

**Phase 2C — Variant Expansion**:
New Reynolds numbers, geometries, coupling strengths on the above. Three-track leaderboard (Monolithic / Composition / Specialist-Only).

### Phase 3: 3D Multi-Physics & Advanced Composition

- 3D FSI (cylinder/flap with turbulence)
- 3D Thermo-Elasticity (bimetal, engine, turbine components)
- 3D CHT (electronics, battery, turbine cooling)

Requires 3D turbulence bridge (proper Kolmogorov spectrum initialization, not simple zero-pad), 3D-specific gates (energy spectrum, Q-criterion, wall shear, Nusselt distribution), and curriculum from 2D specialists.

Reference solutions: preCICE partitioned, FEniCS/OpenFOAM monolithic where appropriate.

---

## 3. Validation Strategy — Scientific Rigor & Competitive Edge

### 3.1 Multi-Objective Scoring (45/30/25)

Final combined score = w_p · PhysicsFidelity + w_r · Robustness + w_a · Accuracy, with w = [0.45, 0.30, 0.25].

Only new best combined scores on a challenge receive strong weight from the ChallengeWinnerTracker.

**Physics Fidelity (45%)**:
- Residual norms (PDE residual, divergence error for incompressible flow)
- Conservation errors (mass, momentum, energy)
- Boundary condition satisfaction (relative L2 or max norm)
- Stability metrics (energy growth/decay rates, rollout stability)

**Robustness (30%)**:
- Performance degradation under hidden stress (procedural + data-driven)
- Long-horizon rollout stability
- Generalization across parameter variations and out-of-distribution slices

**Accuracy (25%)**:
- Hold-out / benchmark error (relative L2, max error)

### 3.2 Physics Gates (Enforcement Layer)

**Hard Gates** (score = 0 on violation — non-negotiable physical constraints):
- Mass conservation: ‖∇·u‖ / ‖u‖ < threshold (typically 1e-3)
- Energy dissipation/stability: |dE/dt| or long-term energy drift below threshold
- Boundary satisfaction: relative error on Dirichlet/Neumann conditions
- Rollout stability: bounded energy growth over long horizons
- UQ calibration (when applicable)

Phase-field specific: crack irreversibility (∂d/∂t ≥ 0), length-scale consistency, valid degradation function.

**Soft Gates** (multiplicative penalty):
- Symmetry violation, spectral fidelity, conservation drift (graded penalties).

These gates are designed so that a PhD-level reviewer can verify they correspond to fundamental physical requirements of the PDE class.

### 3.3 Hidden Stress Testing (Adversarial Robustness — Core Moat)

Stress is generated per physics class with explicit scientific justification. Number of variants and parameter ranges scale with difficulty. All variants carry `physics_justification` metadata.

**Elliptic (Poisson/Darcy)**:
- Source amplitude & spatial variation (tests maximum principle & conservation)
- Boundary condition strength/type variation
- Coefficient field regularity (smooth → discontinuous; tests solution regularity)

**Hyperbolic (Burgers)**:
- Shock strength (initial condition steepness)
- High-frequency perturbation amplitude (tests shock capturing & stability)
- Rollout horizon length (long-time behavior after shock formation)
- Viscosity variation (within physically relevant range)
- Initial condition noise

**Parabolic (Heat)**:
- Time-dependent forcing amplitude & frequency
- Conductivity field variation
- Rollout length (long-term decay)
- Initial condition roughness

**Incompressible Flow (NS laminar)**:
- Reynolds number (laminar regime)
- Geometry scale/perturbation
- Boundary condition perturbation
- Initial vorticity noise
- Weak body forcing

**Elasticity**:
- Young's modulus variation
- Poisson ratio range
- Boundary displacement magnitude
- Material anisotropy
- Body force strength

**Thermo-Elasticity (Multi-physics)**:
- Thermal expansion coefficient
- Thermo-mechanical coupling strength
- Temperature loading amplitude
- Mechanical damping
- Deformation-induced heat source strength

**Difficulty Scaling**: Higher difficulty increases number of variants, range of parameter excursions, and rollout lengths while remaining physically plausible.

**Data-Driven Stress (The Well)**: Relevant dataset slices (turbulence, viscoelastic, active matter, acoustic scattering, etc.) mapped to physics class. Physics-preserving augmentations applied where possible.

**Strategic Advantage**: Hidden adversarial stress testing is extremely difficult for centralized platforms to match at scale. It forces genuine robustness and provides verifiable, trustless evaluation — a major credibility advantage for engineering and regulated applications.

See `docs/STRESS_TEST_DESIGN.md` and current `neurons/stress/procedural_generator.py` for exact parameter ranges and justification strings.

---

## 4. Determinism & Reproducibility (Scientific Trust & Credibility Moat)

Every evaluation must be reproducible given only public inputs + validator identity. Hierarchical seeding + framework controls achieve this.

Master seed derived from challenge_id + validator hotkey. Sub-seeds control data loading, augmentation, training, stress generation, and scoring.

PyTorch determinism flags + environment provenance recording enable cross-validator verification. A Reproducibility Harness compares scores, key tensors (within tolerance), and gate outcomes.

**Strategic Importance**: This level of determinism is required for credible claims of robustness and for audit/dispute resolution. It provides a trustless verification layer that centralized "black-box" AI platforms struggle to match, especially in safety-critical or regulated domains.

---

## 5. Landscape Agent — Symbolic & Causal Compounding (Core Innovation Engine)

The Landscape Agent is the component that turns decentralized evaluation into collective intelligence — enabling Carbon to discover better *ways* to train Neural Operators.

**Ingestion**: StrategyFragments containing strategy config, training metrics, full stress results (per-variant performance + gate outcomes), and symbolic features.

**Symbolic Processing**: Enrichment with conservation laws, symmetries, boundary types, coupling terms (extracted via rule-based Phase 0; ModelingToolkit + PySR in later phases).

**Causal Analysis**: Double Machine Learning (DML) to estimate heterogeneous treatment effects of strategy features (loss weights, backbone choice, curriculum parameters, etc.) on outcomes (combined score or robustness). This is central to discovering which training methodologies actually work.

**Knowledge Compounding**: Updated priors, causal graphs, and performance history are used to generate better challenge priors and specialist candidates. This creates compounding returns on every evaluation submitted to the network.

**Outputs**: Improved agent priors, specialist distillation candidates, causal insights for roadmap/challenge design, inputs to Symbolic Gauntlet.

**Strategic Role**: This is how Carbon turns parallel exploration into superior methodologies faster than centralized teams. The compounding effect (better data → better insights → better strategies → richer data) is a core part of the thesis that a decentralized subnet can outperform centralized players.

**Future**: Integration with multi-physics composition and Foundation Operator (LPM with FiLM conditioning, evidential UQ).

See design notes for DML implementation sketch and data schemas.

---

## 6. Detailed Implementation Components

(See current code in `neurons/` for reference implementations that match the interfaces below.)

**Stress Generators**: Registry-based with physics-class-specific deep implementations (parameter variation logic as described in Section 3.3).

**StressEvaluator**: Runs model on StressTestSet, applies gates, returns structured results (hard failures, soft penalties, per-variant metrics, stress contribution).

**HydrogenScorer**: Integrates base metrics + stress results; computes weighted scores; modulates final combined score by stress contribution.

**generate_challenge()**: Deterministic function returning Challenge object with training/holdout references, stress_config, and attached SymbolicMetadata.

**MCP Layer**: Handles strategy submission, streaming results, and built-in testing endpoints.

---

## 7. Phased Roadmap (Build-Level)

**Phase 0**:
- Stress generators (procedural deep per class + Well) with determinism.
- StressEvaluator + full scoring integration.
- Determinism utilities and reproducibility harness.
- MCP basics + testing loop.
- Symbolic extractor + PySR skeleton.
- ChallengeWinnerTracker.
- generate_challenge() with symbolic attachment.

**Phase 1**:
- Abaqus ODB/.fil parser (mesh + field outputs: stress/strain/displacement/history).
- CustomDataset mixing with procedural data.
- Initial Landscape Agent (DML causal updates + symbolic enrichment).
- Expanded determinism in data paths.

**Phase 2**:
- preCICE orchestration for FSI (Turek/Hron) and CHT benchmarks.
- Thermo-elasticity reference generation (~48 cases, mesh-converged FEniCS).
- Specialist pipeline schema + execution.
- Three-track leaderboard and stress testing on multi-physics problems.

**Phase 3**:
- 3D turbulence initialization (Kolmogorov spectrum) and 3D-specific gates (energy spectrum, Q-criterion, wall shear, Nu).
- 3D FSI/CHT/Thermo-elasticity with appropriate references (preCICE, OpenFOAM, FEniCS).
- Advanced Landscape Agent outputs and Foundation Operator foundations.

---

## 8. Scientific Defensibility & Competitive Differentiation

Every stress dimension is chosen because it directly probes a fundamental physical property of the PDE class (conservation, stability, shock capturing, coupling strength, etc.). Hard gates correspond to non-negotiable physical requirements. The Landscape Agent's causal analysis provides interpretable insights into what actually improves physical fidelity and robustness. Determinism ensures results are reproducible and auditable by domain experts.

**Competitive Positioning**:

The broader industry is rapidly advancing toward **Software Defined Machines** and **Living Digital Twins**, where high-fidelity models serve as the single source of truth across the entire product lifecycle — from design and embedded control to ongoing operation and predictive maintenance, continuously refined by real-world sensor data. Leading platforms such as JuliaHub’s Dyad are building modern acausal modeling environments, deep SciML integration (neural surrogates, model discovery, differentiable programming), generative AI assistance, and cloud-native deployment workflows to realize this vision for industrial engineering (aerospace, automotive, energy, etc.).

**Carbon plays a distinct and complementary role** in this ecosystem:

- While centralized platforms focus on usability, integration, model generation, and accelerating surrogate creation within a single environment, Carbon is the **decentralized discovery and robustness engine**.
- Carbon enables massively parallel exploration of Neural Operator training strategies across a global network of agents and miners.
- It applies rigorous, hidden adversarial stress testing with physics-class-specific gates that centralized systems struggle to replicate at scale.
- The Landscape Agent extracts symbolic features and causal relationships, turning individual evaluations into compounding collective intelligence about *how* to best train and validate these surrogates.

This makes Carbon particularly valuable for producing surrogates that are not only fast but genuinely robust, physically trustworthy, and auditable — critical for safety-critical and regulated applications within the Software Defined Machines and Living Digital Twins paradigm.

In essence: Platforms like Dyad modernize the modeling and surrogate *environment*; Carbon discovers and validates the superior *methodologies* that power higher-performing, more reliable digital twins across the network.

A PhD reviewer should be able to verify that the system is not merely optimizing for benchmark scores but is enforcing and learning physically meaningful behavior while leveraging decentralized parallel exploration to innovate faster than centralized alternatives.

---

*This specification is written to be scientifically rigorous and buildable. Reference the implementation in `neurons/` and supporting design documents for concrete code.*
