# SPEC.md — Carbon PDE Subnet Technical Specification (Buildable Level with Strategic Emphasis)

**Version:** 5.0 (Updated July 2026) — **Final Miner Loop + Data Handling Design**
**Audience**: Researchers and engineers with PhD-level background in Physics, Computational Mechanics, or Scientific Computing.

This specification provides sufficient detail for a domain expert to understand the scientific rationale, implementation logic, and expected behavior of every major component. It is intended to be buildable and scientifically defensible.

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
- Miner Toolkit Docker image with local support.
- Noisy prior distribution.
- Estimation Mode (noisy-prior based).
- Light Training templates + local multi-fidelity evaluation.
- Direct submission path.
- Basic cost estimation.

**Phase 1**:
- Cloud rental integration (Targon + Chutes first).
- Python SDK for agents.
- Improved defaults and templates.
- Strategic guidance integration.

---

*This specification is written to be scientifically rigorous and buildable. Reference the implementation in `neurons/` and supporting design documents for concrete code.*
