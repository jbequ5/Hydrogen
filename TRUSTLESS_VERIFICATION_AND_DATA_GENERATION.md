# TRUSTLESS_VERIFICATION_AND_DATA_GENERATION.md

**Carbon PDE Subnet — Trustless Verification & Data Generation System**

**Version:** 1.0 (July 2026)
**Status**: Core Design Document

This document defines Carbon’s approach to generating evaluation data (both for stress testing and benchmarking) in a way that is **trustless, auditable, unpredictable to miners, and scientifically credible**.

---

## 1. Philosophy & Goals

Carbon aims to replace "trust the team not to leak or pre-know the test data" with **"trust the open math and public seeding anyone can inspect."**

### Core Goals
- **Trustless**: No single party (including the subnet team) can pre-know or control the exact evaluation instances.
- **Auditable**: Anyone can inspect the generator and verify that the system is fair.
- **Unpredictable**: Miners and agents cannot reliably overfit or prepare for the exact data used in official evaluations.
- **Scientifically Credible**: The data used for benchmarking must be high-quality and physically meaningful.
- **Agent-Friendly**: The system should provide useful signal for local/agent iteration without compromising the hidden nature of official evaluations.

This approach aligns with Carbon’s broader thesis of being objective, verifiable, and decentralized rather than authority-based.

---

## 2. Core Mechanism: Open Procedural Generator + Public Unpredictable Seeding

### 2.1 Open Generator
The `ProceduralStressGenerator` (and per-physics subclasses) is fully open-source, versioned, and part of the public specification. Every parameter range and generation rule has documented scientific justification.

### 2.2 Public Unpredictable Seeding
Evaluation data is generated **at runtime inside the validator** using a seed derived from public, unpredictable information that no single party controls in advance.

**Phase 0 Seeding**:
```python
master_seed = hash(challenge_id + block_hash + validator_hotkey + run_nonce)
```

**Phase 1+ Direction**:
Move toward a lightweight commit-reveal scheme layered on top of the block hash for stronger collusion resistance.

All sub-seeds (data generation, stress parameters, etc.) are deterministically derived from the master seed. This ensures reproducibility while keeping the actual instances hidden until validation time.

### 2.3 Freshness
Because the seed incorporates live blockchain information, the exact stress sets and benchmark instances are different on every validator run. This prevents pre-computation and makes overfitting extremely difficult.

---

## 3. Benchmark Data Quality & Credibility

A key requirement is that procedurally generated data used for **official benchmarking** (the Accuracy component of scoring) must be scientifically credible.

### 3.1 How Quality Is Proven
We do **not** rely on fixed known reference datasets as the primary benchmark data (this would weaken the trustless property).

Instead, quality is established through:

- **Strong Scientific Justification**: Every parameter range, distribution, and generation rule in the ProceduralStressGenerator is documented with references to physics literature, known regimes, and expected behaviors (shock formation, conservation, stability, etc.).
- **Generator Validation**: We periodically sample procedurally generated cases and compare them against independent high-fidelity solvers (FEniCS, OpenFOAM, etc.). Validation results are published or made available for audit.
- **Physics Gates as Independent Filter**: Hard physics gates (mass conservation, energy stability, boundary satisfaction, rollout stability, etc.) act as an objective quality check. Models that perform well on the data but violate fundamental physics are heavily penalized.

This approach keeps data generation trustless and unpredictable while providing credible quality through transparent justification and validation of the *generator*, not through fixed known datasets.

### 3.2 Hybrid Elements (Optional Enhancement)
A small number of high-quality reference solutions may be maintained for generator validation purposes only. These are **not** used as the primary benchmark data for scoring.

---

## 4. Local / Agent Test Runs vs Official Validator Evaluation

### 4.1 Separation Principle
Local test runs and agent iteration loops must provide useful signal without leaking information about the official hidden evaluation distribution.

### 4.2 Implementation
- **Official Validator Mode**: Full hidden stress + benchmark data generated with the public unpredictable seed. Full physics gates applied.
- **Local / Test Mode** (for miners and agents):
  - Uses the **same open generator**.
  - Uses different seeds or deliberately reduced variant sets.
  - Can apply full hard physics gates for signal quality.
  - Clearly documented as "local evaluation mode" with lower weight when contributing to the Landscape Agent.

This gives agents a consistent, high-quality evaluation surface for fast iteration while maintaining a hard information barrier between local loops and official scoring.

---

## 5. Gaming Resistance

Even with hidden seeds, sophisticated agents could attempt to learn the generator’s behavior over many runs.

### 5.1 Layered Defenses (Phase 0+)
1. **Versioned Generator Releases**: Deliberate changes to distributions and new stress dimensions in new versions force re-learning.
2. **Controlled Noise Injection**: On non-critical parameters.
3. **Adaptive Difficulty**: Network-wide performance can gradually increase stress intensity.
4. **Black-Box Diagnostics + Multi-Fidelity**: Limits information leakage (already planned).

These layers make systematic gaming expensive and slow.

---

## 6. Audit Surface & Credibility

To make the system extremely credible, the following artifacts are provided:

- Full open-source `ProceduralStressGenerator` code with scientific justification.
- Clear **Seeding Specification** (how master seeds and sub-seeds are computed).
- **Threat Model** document outlining considered attacks and mitigations.
- Published validation results comparing the generator against high-fidelity reference solvers.
- Version history and changelogs for the generator.

Anyone (including domain experts) can audit that the system is fair without needing to trust any single party.

---

## 7. Phased Implementation

**Phase 0**:
- Open ProceduralStressGenerator with scientific justification
- Public seeding using Challenge ID + Block Hash + Validator Hotkey
- Integration into validator evaluation (stress + benchmark data)
- Local mode separation for agent/miner test runs
- Basic documentation and threat model

**Phase 1**:
- Lightweight commit-reveal seeding layer
- Stronger generator validation pipeline against reference solvers
- Versioned generator releases with deliberate distribution changes
- Enhanced strategic guidance from the Landscape Agent using generator insights

**Phase 2+**:
- Full commit-reveal + advanced gaming resistance mechanisms
- Cross-domain causal analysis of generator behavior
- Potential formal verification of key generator properties

---

## 8. Relationship to Other Systems

- **HydrogenScorer & Physics Gates**: Act as independent quality filters on top of generated data.
- **Landscape Agent**: Can analyze generator behavior and extracted symbolic features across evaluations.
- **Miner Toolkit & Estimation Mode**: Use the same open generator (with different seeds) for fast local screening.
- **MCP Layer**: Black-box diagnostics protect the hidden nature of official evaluations while still providing useful signal.

---

*This system is a core part of Carbon’s trustless verification mechanism. It enables scalable, low-friction iteration for both humans and autonomous agents while maintaining scientific rigor and long-term defensibility.*
