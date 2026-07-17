# Hydrogen: Bittensor Subnet for Physical Intelligence

**A decentralized, incentive-aligned system for compounding knowledge about training physics-informed neural operators (PINO, FNO, DeepONet, etc.).**

Physics ML has the right architectures (discretization-invariant neural operators) and libraries (PhysicsNeMo, NeuralOperator). What it lacks is a system that turns tribal training tricks into verifiable, compounding, physics-enforced progress.

Hydrogen makes **physics the hard constraint** (binary gates on mass conservation, energy dissipation, rollout stability, UQ calibration, boundaries) and uses causal inference + symbolic reasoning to discover *what actually works* across PDE families.

Miners submit training strategies (JSON configs), never weights or GPUs. Validators run pinned, reproducible environments and enforce physics. The Landscape Agent runs Double ML on every submission to extract causal effects and evolve better baselines. Winning strategies are distilled into composable, symbolically-annotated ONNX specialists.

## Current Status (July 2026)

- **Phase 0 MVP in active development**: Core flywheel (challenges → strategy submission → physics-gated validation → causal baseline updates).
- Starting with 3 single-physics PDEs (Poisson 2D, Darcy 2D, Burgers) for rapid iteration on reproducibility, determinism, and incentive mechanics.
- Full vision (7+ PDEs, multi-physics composition, 3D turbulence bridge, Foundation Operator/LPM, edge HIL, agent swarms) remains the north star but is gated behind working Phase 0.
- Repo contains detailed specs + appendices. Implementation scaffolding underway.

## Key Innovations

- **Hard Physics Gates**: Binary pass/fail (no "good enough"). Score = 0 on failure.
- **Causal Knowledge Compounding**: Landscape Agent uses Double ML on StrategyFragment DAG to estimate `P(improvement | do(param))` instead of correlations.
- **Symbolic Layer**: Pre-computed metadata (symmetries, conservation laws, suggested loss weights) from ModelingToolkit.jl principles. Auto loss weighting and future acausal composition / codegen.
- **Incentive Alignment**: Top-4 per challenge (40/30/20/10) + novelty/symbolic bonuses. Submission fees. Validators paid for reliable physics checks.
- **Agent-Native Future**: DID + A2A protocols, swarms, reputation (deferred to post-Phase 0).

## Getting Started (Phase 0 MVP)

See `SPEC.md` for the authoritative technical specification (miner/validator interfaces, physics gates, scoring, Landscape, emission mechanics).

See `roadmap.md` for phased milestones and exit criteria.

**For miners**: Lightweight CLI + Python SDK (coming in initial scaffolding). Submit strategy JSONs. No GPU required.

**For validators**: Pinned Docker images (`hydrogen/validator:pino-v0.1` etc.) with deterministic training harness. 3+ validators for median consensus.

**For researchers/agents**: Structured feedback includes physics gate breakdown, causal insights from Landscape, and suggested improvements.

## Repository Structure (Current)

- `README.md` — This file (vision + status).
- `SPEC.md` — Consolidated technical specification (deduplicated, Phase 0 focus + full vision references).
- `roadmap.md` — Execution phases, deliverables, risks, revenue path.
- `Launch_Spec.md` — Legacy Phase 0-focused variant (being aligned into SPEC.md).
- `Appendices/` — Detailed runtime specs (validator, miner CLI, dashboard, dev environment, testing, runbook).
- Implementation code (neurons/, hydrogen/ package, Dockerfiles) being added now.

## Why Bittensor?

The subnet *is* the product. Incentives force optimization for verifiable physics improvement under hidden stress tests. Knowledge compounds autonomously. Barrier to entry is a good idea, not a GPU cluster.

## Market Opportunity

Real-time physics surrogates for aerospace, automotive, energy, manufacturing, biomedical, robotics. TAM $135B+ for edge HIL + digital twins. Dual-licensed specialists (AGPL-3.0 + commercial) + data royalties + composition engine licensing.

## Contributing & Contact

Active development. Issues and PRs welcome once core scaffolding lands.

X: @dTAO_Dad
GitHub: jbequ5/Hydrogen

*Hydrogen: Where every training run teaches the network. Physics is the only metric that pays.*