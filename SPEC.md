# SPEC.md — Carbon PDE Subnet Technical Specification (Buildable Level with Strategic Emphasis)

**Version:** 5.1 (Updated July 2026) — **Initial Design Priorities Locked**
**Audience**: Researchers and engineers with PhD-level background in Physics, Computational Mechanics, or Scientific Computing.

This specification provides sufficient detail for a domain expert to understand the scientific rationale, implementation logic, and expected behavior of every major component. It is intended to be buildable and scientifically defensible.

---

## Initial Design Priorities (Phase 0 Focus)

The following three capabilities are prioritized for the initial design because they directly enable low-friction, scalable iteration while protecting the integrity of the hidden validation system:

### 1. Black-Box Diagnostics with Clear Diagnostic Tiers
MCP diagnostics returned to miners and agents will be deliberately limited. Only objective scores, gate pass/fail status, and high-level category feedback will be provided. Precise geometric, spectral, or spatial hotspot information will not be exposed. This is a core architectural decision to protect the hidden stress distribution and prevent reverse-engineering of the validator’s evaluation data.

Clear diagnostic tiers will be defined early:
- Basic tier: Objective scores + overall gate status
- Intermediate tier: High-level failure categories (e.g., "long-rollout stability", "shock capturing")
- Rich tier: Available only after strong performance or with additional rate-limiting/staking

### 2. Noisy Prior Distribution + Estimation Mode
The system will distribute only noisy / perturbed versions of the current best strategies (never the clean champion). An Estimation Mode will be provided that allows near-zero-cost screening of new strategy ideas using fast approximations anchored to the noisy prior. This enables both human miners and autonomous agents to run fast, Autoresearch-style iteration loops with minimal friction while maintaining strong protection of the collective intelligence moat.

Estimation Mode outputs will be clearly labeled as estimates with confidence scores. They are intended for rapid filtering and idea generation, not as a replacement for actual training or official validator evaluation.

### 3. ModelingToolkit.jl Integration for Structured Losses
PySR symbolic constraints extracted by the Landscape Agent will be compiled into structured loss equations using ModelingToolkit.jl. This integration will be pursued early so that symbolic insights can be turned into concrete, differentiable loss terms that agents can directly use in their local training loops. This significantly increases the actionability of the feedback loop between the Landscape Agent and participating miners/agents.

These three priorities are viewed as foundational for enabling iteration at scale while preserving scientific rigor and long-term defensibility.

---

## Miner Compute, Local Iteration & Submission Model

### 1. Core Philosophy

- The **validator always performs full deterministic training + hidden adversarial stress evaluation** the same way for every submission.
- Miners and autonomous agents run **local iterative training loops** on their own hardware (or rented machines) to improve strategies before submission.
- **Submission is always free**. Local training is an *optional enhancement*, not a requirement.
- The system distributes **noisy priors** only (never the clean champion) to enable compounding while protecting the moat.
- High-quality Landscape knowledge (causal insights, symbolic patterns) is protected and shared selectively via strategic guidance.

### 2. Three-Tier Local System

| Tier                    | Compute Cost      | Anchored To          | Purpose                              | Required Before Submission? | Cost Estimate Provided? |
|-------------------------|-------------------|----------------------|--------------------------------------|-----------------------------|-------------------------|
| **Estimation Mode**     | Near-zero         | Noisy Prior          | Rapid idea screening & filtering     | No                          | Yes (if renting)        |
| **Light Training Mode** | Low               | Noisy Prior          | Main iterative improvement loop      | No (recommended)            | Yes                     |
| **Validator (Official)**| Network-paid      | Full hidden data     | Official scoring + emissions         | Yes                         | N/A                     |

**Key Rule**: A miner can submit a strategy JSON to the validator at any time with zero local training. Training is purely optional to help them submit stronger strategies.

### 3. Data, Stress Tests, and Physics Gates in Internal Mining Loops

#### 3.1 Core Principle
Internal mining loops (Estimation Mode and Light Training Mode) must use **different data and stress conditions** from the validator’s hidden evaluation set. This preserves the adversarial integrity of official scoring while still providing useful signal for iteration.

Miners and agents **never** have access to the validator’s hidden test data or the full hidden stress variant set during local loops.

#### 3.2 Training Data in Local Loops
- Local loops may use procedural data generation and The Well slices.
- Data generation should use different random seeds or subsampling strategies than the validator.
- Custom datasets are allowed if properly validated.
- The goal is to enable meaningful training signal without replicating the validator’s exact data distribution.

#### 3.3 Local Stress Testing and Evaluation
- **Estimation Mode**: Uses fast approximations anchored to the noisy prior. No actual stress rollout is performed.
- **Light Training Mode**: May run a **reduced, non-hidden set** of stress-like variants for local evaluation. These variants must be different from the validator’s hidden stress set.
- Local stress testing should still apply physics-aware metrics (residuals, conservation, stability) for signal quality.
- Full hard physics gates **can** be applied during Light Training Mode for better learning signal, but this does not replace the validator’s official gated evaluation.

#### 3.4 Why This Separation Matters
- Prevents miners from gaming the official hidden stress by tuning against it locally.
- Maintains strong defensibility of the validator pipeline.
- Still allows fast, high-signal local iteration.
- Ensures that only strategies evaluated under the true hidden adversarial conditions receive official credit and emissions.

### 4. Estimation Mode (Noisy-Prior Only)

**Purpose**: Allow very fast, near-zero-cost screening of ideas.

**Rules**:
- Must be based **only on the latest noisy prior** for the challenge + backbone.
- Never uses the clean champion model.
- Returns estimated deltas, confidence, and risk notes.
- Clearly labeled as an *estimate* (not a substitute for actual training).

**Recommended Implementation**:
- Linear / sensitivity-based approximation around the noisy prior.
- Optional small proxy model for improved signal.
- Returns structured output with confidence score.

This mode is ideal for high-volume search by autonomous agents and quick filtering by human miners.

### 5. Local Training (Optional Enhancement)

Miners may optionally run actual training loops starting from the noisy prior:

- **Light Training Mode** (recommended default): Reduced budget with multi-fidelity local evaluation + physics-residual monitoring.
- **Full Local Confirmation**: Longer runs for final validation before submission.

Training is provided as a convenience to improve submission quality. It is not required.

### 6. Submission Model (Zero Friction)

- Miners can submit a strategy JSON to the validator **at any time**.
- No local training is required to submit.
- The validator will perform full training from the submitted JSON + full hidden stress testing + physics gates.
- Only submissions that set a new best combined score on the validator side receive strong weight in the ChallengeWinnerTracker.

### 7. Cost Estimation

When a miner chooses to use rented compute (Targon, Chutes, RunPod, etc.), the Miner Toolkit must provide clear upfront cost estimates before execution.

Examples:
- Light Training on 1× A100 ≈ $X–$Y
- Full local confirmation on 1× H100 ≈ $X–$Y

### 8. Miner Toolkit (Docker Image + Interface)

A dedicated **Miner Toolkit** Docker image will be provided with:

- CLI for easy local and rented execution.
- Python SDK for autonomous agents (propose → train/evaluate → decide → submit).
- Automatic noisy prior loading.
- Templates for common backbones.
- Built-in multi-fidelity local evaluation and physics monitoring.
- Cost estimation for rented providers.

**Target Experience**:
- A novice should be able to start a productive loop in < 5 minutes.
- An autonomous agent should be able to run full iterative loops with minimal custom code.

### 9. Security & Moat Protection

- Only **noisy priors** are distributed.
- The clean champion model is never exposed.
- High-value Landscape knowledge (raw causal graphs, detailed DML outputs) remains protected.
- The rigid validator pipeline (hidden stress + physics gates + progress-only rewards) acts as the primary filter against low-value strategies.
- All official scoring and emissions impact comes exclusively from validator-executed runs.

### 10. Phased Implementation

**Phase 0**:
- Black-box diagnostics with clear diagnostic tiers
- Noisy prior distribution + Estimation Mode (anchored to noisy priors)
- Miner Toolkit Docker image with local support and basic Python interface
- Light Training templates + local multi-fidelity evaluation
- Direct submission path (always available)
- Basic cost estimation for rented compute

**Phase 1**:
- ModelingToolkit.jl integration for turning PySR symbolic constraints into structured loss terms
- Cloud rental integration (Targon + Chutes prioritized)
- Stronger strategic guidance generation from the Landscape Agent
- Initial Abaqus ingestion utilities (scoped)

**Phase 2+**:
- Cross-domain causal mapping via Double Machine Learning
- Advanced agent tooling and multi-asset emissions features

---

## Scientific Motivation & Strategic Positioning

High-fidelity simulation remains the bottleneck in engineering design, optimization, digital twins, and real-time control. Traditional solvers scale poorly with design space size or real-time requirements. Pure data-driven ML surrogates are fast but frequently violate conservation laws, stability conditions, or boundary physics, rendering them unreliable for downstream engineering use.

The space for AI-powered physics simulation and Neural Operators is still **nascent**. There is a tremendous amount left to discover in *how* to best build, train, and use these models for real engineering problems.

Centralized teams explore this space linearly. Carbon is designed to explore it in parallel across thousands of strategies with strong selection pressure from hidden adversarial validation and compounding knowledge via the Landscape Agent.

**Core Thesis**: A properly aligned decentralized subnet can discover superior Neural Operator training methodologies faster and cheaper than centralized players, while providing trustless, verifiable robustness.

---

## Challenges by Phase (Specific Problem Definitions)

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
Same 7 challenges + custom datasets and LoRA/custom strategy support. Initial Abaqus ingestion utilities scoped for mesh + primary field translation.

### 4.3 Phase 2: Verified Multi-Physics Composition
FSI (Turek/Hron), CHT, and expanded Thermo-Elasticity with preCICE and reference solutions.

### 4.4 Phase 3: 3D Multi-Physics & Advanced Composition
3D FSI/CHT/Thermo-elasticity with turbulence, 3D-specific gates, and curriculum from 2D specialists.

---

## Validation Strategy — Scientific Rigor & Competitive Edge

Multi-objective scoring (45/30/25), hard/soft physics gates, and hidden stress testing. Multi-fidelity and uncertainty-aware extensions enhance throughput and sophistication.

---

## Determinism & Reproducibility
Hierarchical seeding and Docker-based reproducibility harness ensure all training, stress testing, and scoring are reproducible and auditable.

---

## Landscape Agent — Symbolic & Causal Compounding
Ingests results and Model Cards from production and high-quality test runs. Extracts symbolic features and applies causal analysis to discover effective training methodologies. ModelingToolkit.jl integration will be used to turn extracted symbolic constraints into structured, usable loss terms.

---

## Detailed Implementation Components
- Stress Generators & StressEvaluator (multi-fidelity support)
- HydrogenScorer
- Backbone Registry (dynamic instantiation from JSON)
- Validator Docker image (model card generator, residual monitoring)
- MCP layer (black-box diagnostics with tiers, noisy prior distribution, Estimation Mode support)
- Miner Toolkit (local training templates, Estimation Mode, cost estimation)
- generate_challenge()
- Reproducibility Harness

---

## Phased Roadmap (Build-Level)

**Phase 0**:
- Black-box diagnostics with clear diagnostic tiers
- Noisy prior distribution + Estimation Mode
- Miner Toolkit Docker image
- Light Training templates + local multi-fidelity evaluation
- Direct submission path
- Basic cost estimation

**Phase 1**:
- ModelingToolkit.jl integration for structured losses from PySR
- Stronger strategic guidance from Landscape Agent
- Initial scoped Abaqus ingestion
- Cloud rental integration (Targon + Chutes first)

**Phase 2+**:
- Cross-domain causal mapping
- Advanced agent tooling
- Multi-asset emissions features

---

## Scientific Defensibility & Competitive Differentiation
All extensions are designed to be scientifically grounded, reproducible, and auditable while enabling faster discovery of superior Neural Operator training methodologies.

---

*This specification is written to be scientifically rigorous and buildable. Reference the implementation in `neurons/` and supporting design documents for concrete code.*
