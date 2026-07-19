# Hydrogen

**Decentralized Discovery of Physics-Informed Neural Operator Strategies**

Hydrogen is a Bittensor subnet (SN63) building a decentralized network for discovering high-quality, physics-respecting training strategies for complex engineering simulations.

At its core, Hydrogen combines **adversarial evaluation**, **strong physics constraints**, and **decentralized strategy iteration** to produce fast, robust neural operator surrogates that outperform both traditional high-fidelity solvers (in speed) and black-box ML models (in physical consistency).

---

## Vision

To create a living, evolving library of reusable, physics-grounded surrogate models and specialists that dramatically accelerate engineering design, digital twins, real-time simulation, and scientific discovery — built through decentralized, adversarial, physics-constrained competition rather than centralized lab efforts.

Longer term, Hydrogen aims to contribute to **foundational models of physics**: systems that can generalize across domains (fluids, solids, electromagnetics, plasmas, quantum-informed problems, etc.) while maintaining rigorous physical consistency.

---

## Value Proposition

Traditional engineering simulation is slow and expensive for large design spaces or real-time use. Pure data-driven ML surrogates are fast but often lack physical trustworthiness.

Hydrogen produces **physics-informed neural operator surrogates** that are:

- **Fast** — orders of magnitude faster than traditional solvers once trained
- **Physically consistent** — trained and stress-tested against hard physics constraints (conservation, stability, boundary conditions, energy dissipation, etc.)
- **Robust** — evaluated under hidden stress conditions and adaptive difficulty, making gaming and overfitting much harder
- **Discoverable at scale** — decentralized competition surfaces better strategies than any single lab could reasonably explore

This combination is particularly valuable in:
- Real-time digital twins
- Large-scale design optimization and generative design
- Hardware-in-the-Loop (HIL) testing
- Multi-physics problems where traditional solvers become prohibitively slow
- Regulated or safety-critical domains that demand physical fidelity

---

## How It Works (Core Design)

Hydrogen’s architecture rests on several interlocking principles:

### 1. Multi-Objective Physics-Gated Scoring
Every submission is scored across three high-level objectives:

- **Physics Fidelity** (45%) — residuals, conservation, boundary conditions, stability
- **Robustness** (30%) — performance under hidden stress and long-term rollout
- **Accuracy** (25%) — benchmark / hold-out performance

Only strategies that beat the current best **combined score** on a challenge receive meaningful weight. Everything else is heavily discounted.

### 2. ChallengeWinnerTracker (Per-Challenge Leader Tracking)
Inspired by Minos-style round-only winner logic but extended across multiple challenges:

- Tracks the best combined score **per challenge**
- Applies exponential decay on old performance
- Produces winner-heavy + participation dust weight distributions
- Only genuine new leaders (on the combined physics + robustness + accuracy metric) drive emissions

### 3. Decentralized Strategy Discovery
Miners/agents propose training strategies (backbones, loss weights, curricula, architectures, etc.). The network adversarially evaluates them under hidden conditions. Better strategies rise. The Landscape Agent extracts causal insights and improves priors over time.

### 4. Information Asymmetry (Anti-Gaming)
Miners and agents see challenge descriptions, their own scores, and noisy/aggregated priors — but **not** the hidden stress conditions, exact physics gate implementations, or full internal scoring logic. This asymmetry is intentional and core to robustness.

### 5. Reusable Specialists & Composition (Future)
Over time, high-performing strategies are distilled into reusable ONNX specialists with validity domains. These can be composed into multi-physics pipelines. The Specialist Bank + data royalty model creates a flywheel of reusable, verified components.

---

## Current State (July 2026)

Hydrogen has completed its foundational Phase 0 infrastructure:

- `ChallengeWinnerTracker` with exponential decay and participation dust
- `StrategyStore` abstraction + local file implementation
- Multi-objective `HydrogenScorer` (Physics / Robustness / Accuracy)
- Validator with dry-run mode and basic monitoring
- MCP server with persistent sessions, streaming validation, and Pareto support
- Rich per-evaluation data export for the Landscape Agent

Emissions currently follow standard Yuma Consensus. A hybrid model with Breakthrough Bounties and Decaying Stipends is planned but not yet active.

See `SPEC.md` for the detailed technical specification and `docs/FUTURE_DOMAINS.md` for the expansion roadmap.

---

## Future Domains & Expansion Roadmap

Hydrogen is designed to expand across high-value physics and engineering domains. See the full analysis in `docs/FUTURE_DOMAINS.md`.

**Tier 1 (Near-to-Medium Term)**
- Electromagnetics
- Photonics & Optics (including quantum photonics bridge)
- Acoustics & Wave Propagation
- Phase-Field Modeling & Materials Damage/Fracture

**Tier 2 (Strategic)**
- Plasmas & Magnetohydrodynamics (especially fusion-relevant)
- Quantum-informed & hybrid classical-quantum modeling
- Verified multi-physics composition as a core capability

**Tier 3 (Longer-Term / Scientific)**
- Gravity (Newtonian + General Relativity)
- Climate & Earth System Modeling
- Nuclear / Radiation Transport
- Biological & Biomechanical Systems

Cross-cutting themes include real-time/HIL-capable surrogates, digital twins, uncertainty quantification at scale, and composable physics-informed specialists.

---

## Documentation

| Document | Description |
|----------|-------------|
| `SPEC.md` | Full technical specification and architecture |
| `docs/FUTURE_DOMAINS.md` | Future domains, how they fit, why they matter, and market context |
| `docs/VALIDATOR_GUIDE.md` | How to run and understand the validator |
| `docs/EMISSIONS.md` | Current emissions model (standard Yuma) and planned hybrid direction |
| `docs/AGENT_USAGE.md` | MCP / Agent interaction guide and information asymmetry principles |

---

## Getting Started

```bash
# Clone
git clone https://github.com/jbequ5/Hydrogen.git
cd Hydrogen

# Install dependencies
pip install -r requirements.txt

# Run validator in dry-run mode (recommended first)
python neurons/validator.py --dry_run true
```

See `docs/VALIDATOR_GUIDE.md` for configuration options and monitoring.

---

## Contributing

Contributions are welcome. Areas of particular interest:
- New challenge definitions and physics gate implementations
- Improvements to the ChallengeWinnerTracker and scoring logic
- Agent tooling and MCP server enhancements
- Documentation and examples

Please open an issue or pull request.

---

## License

MIT License

---

*Hydrogen is an experiment in decentralized, physics-constrained scientific discovery. The goal is not just better surrogates — it is a new way to explore and encode physical knowledge at scale.*
