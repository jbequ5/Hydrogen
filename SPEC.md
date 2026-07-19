# SPEC.md — Hydrogen PDE Subnet Technical Specification (Buildable Level)

**Version:** 4.0 (Updated July 2026)
**Status:** Active Development — Buildable Reference

This document provides build-level detail sufficient to implement the core Hydrogen system. It includes data models, interfaces, algorithms, flows, and integration points.

---

## 1. System Overview & Core Agentic Loop

**High-Level Flow**:
1. Agent/Miner submits strategy JSON via MCP.
2. Validator retrieves strategy, sets up determinism (master seed from challenge_id + validator hotkey).
3. Deterministic training on challenge data.
4. Hidden StressTestSet generation & evaluation.
5. Physics gate application + multi-objective scoring.
6. Results + diagnostics returned to agent via MCP.
7. Full evaluation data (including stress results and symbolic features) ingested by Landscape Agent.
8. Landscape Agent performs symbolic extraction + causal analysis (DML) and updates knowledge base/priors.
9. Tracker updated; weights computed and submitted (Yuma).

**Key Components**:
- MCP Server (agent communication, testing loop, streaming).
- Validator (orchestration, determinism, stress generation, scoring).
- HydrogenScorer + StressEvaluator.
- ChallengeWinnerTracker.
- Landscape Agent (symbolic + causal compounding).
- Stress Generators (Procedural + Well, registry-based).
- Symbolic Layer (extractor + PySR runner).

---

## 2. MCP / Agent Interface & Built-in Testing Loop

**Purpose**: Make participation seamless for autonomous agents and humans with fast iteration.

**Core Features**:
- Persistent sessions (stateful agent-validator interaction).
- Streaming validation and results (real-time feedback during evaluation).
- Built-in testing loop: Agents can request evaluation on subsets of challenges, specific stress tiers, or local dry-runs.
- Strategy submission format (JSON with backbone, loss weights, curriculum, custom_data, etc.).
- Result format: Scores, gate violations, detailed metrics, diagnostics, symbolic features.

**Implementation Notes**:
- MCP server handles authentication (hotkey-based), session management, and streaming (e.g., via WebSocket or gRPC).
- Agents can call testing endpoints to evaluate strategies without full network weight impact.
- Supports both synchronous and asynchronous submission modes.

See related design notes in conversation history for exact message schemas (to be formalized in v4.1).

---

## 3. Data Models (Core)

**StressVariant**:
```python
@dataclass
class StressVariant:
    variant_id: str
    source: StressSource  # PROCEDURAL | WELL | ADVERSARIAL
    parameters: Dict[str, Any]
    well_dataset: Optional[str] = None
    difficulty: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)  # includes physics_justification
```

**StressTestSet**:
```python
@dataclass
class StressTestSet:
    challenge_id: str
    seed: int
    physics_class: str
    variants: List[StressVariant]
    difficulty_level: float
    total_variants: int
    generation_config: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**SymbolicMetadata**:
```python
@dataclass
class SymbolicMetadata:
    challenge_id: str
    symmetries: List[str] = field(default_factory=list)
    conservation_laws: List[str] = field(default_factory=list)
    boundary_types: List[str] = field(default_factory=list)
    coupling_terms: List[str] = field(default_factory=list)
    dimensionless_groups: List[str] = field(default_factory=list)
    extracted_at: str = ""
    version: str = "v0.1"
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Challenge** (from generate_challenge):
Includes training/holdout references, stress_config, symbolic_metadata, difficulty, etc.

**SymbolicRegressionResult** (from PySR):
```python
@dataclass
class SymbolicRegressionResult:
    equation: str
    complexity: int
    score: float
    loss: float
    metadata: Dict[str, Any]
```

---

## 4. Determinism System (Buildable Details)

**Master Seed Derivation**:
```python
def get_master_seed(challenge_id: str, validator_hotkey: str) -> int:
    combined = f"{challenge_id}:{validator_hotkey}"
    return int(hashlib.sha256(combined.encode()).hexdigest(), 16) % (2**32)
```

**Sub-seeds**:
```python
def get_sub_seeds(master_seed: int) -> Dict[str, int]:
    # Returns dict with keys: data_loading, augmentation, training, stress_generation, noise, scoring
```

**Setup Functions**:
- `setup_pytorch_determinism(seed)`: Sets torch.manual_seed, cuda seeds, use_deterministic_algorithms(True), cudnn flags, environment variables.
- `get_data_loader_generator(seed)`: Returns seeded torch.Generator for DataLoader shuffling.
- `setup_determinism_for_component(component, master_seed)`: Convenience wrapper.

Applied at: Validator evaluation start, stress generation, scoring, and any training/augmentation steps.

**Reproducibility Harness**: Run evaluation twice and compare scores, tensors (within tolerance), and gate outcomes. Log full environment (Docker digest, package versions, CUDA/cuDNN, git commit).

See docs/DETERMINISM_DESIGN.md for full spec.

---

## 5. Stress Test System (Buildable)

**Generators**:
- `BaseStressGenerator` abstract class with `generate(challenge_id, physics_class, seed, difficulty) -> List[StressVariant]`.
- `StressGeneratorRegistry`: Maps physics_class to list of generators.
- `ProceduralStressGenerator`: Deep implementations per physics class (see current code for parameter variation logic per elliptic/hyperbolic/parabolic/incompressible/elasticity/multi-physics).
- `WellStressGenerator`: Dataset mapping + sampling with physics-preserving augmentations.

**Generation**:
- Use sub-seed for stress_generation.
- Scale number of variants and parameter ranges with difficulty.
- Attach rich metadata (physics_justification) to every variant.

**Access Control**: Store raw StressTestSet in validator-private storage. Only final scores/gate results exposed via MCP.

**Audit**: Any validator can regenerate exact set from challenge_id + validator hotkey + recorded generation_config.

See `neurons/stress/` implementation and docs/STRESS_TEST_DESIGN.md.

---

## 6. Validation Pipeline (Step-by-Step Buildable Flow)

1. Receive strategy via MCP.
2. Derive master_seed and sub_seeds.
3. Call `setup_pytorch_determinism(sub_seeds["training"])`.
4. Load/generate Challenge (training/holdout + stress_config + symbolic_metadata).
5. Train model deterministically.
6. Generate StressTestSet using generators + sub_seeds.
7. Evaluate model on stress variants via StressEvaluator.
8. Apply hard gates (zero score on violation) and soft gates.
9. Compute multi-objective scores.
10. Return detailed results via MCP.
11. Ingest full data (config, metrics, stress results, symbolic features) to Landscape Agent.
12. Update ChallengeWinnerTracker.

**StressEvaluator**:
- Accepts model + StressTestSet (+ optional master_seed).
- Runs inference on variants (real implementation replaces simulation).
- Calls scorer.check_hard_gates() and apply_soft_gates().
- Computes stress_score_contribution (0 on hard failure).

See current `neurons/validator.py`, `HydrogenScorer`, and `StressEvaluator` for reference implementations.

---

## 7. Scoring Details

**Objectives**:
- Physics Fidelity (45%): Residual norms, conservation errors, boundary violations, stability metrics.
- Robustness (30%): Stress performance, rollout stability, generalization.
- Accuracy (25%): Holdout/benchmark error.

**Combined Score**: Weighted average, modulated by stress contribution (e.g., combined *= (0.7 + 0.3 * stress_contribution)).

Hard gates zero the overall score on critical violations. Soft gates reduce sub-scores.

See `HydrogenScorer.evaluate_with_stress()` implementation.

---

## 8. ChallengeWinnerTracker

Per-challenge best combined score tracking.
Exponential decay (default 0.85) on historical performance.
Winner-heavy weighting + participation dust.
Only new best combined scores update leader significantly.

See current implementation and docs for exact update logic.

---

## 9. Landscape Agent (Buildable Architecture)

**Ingestion**:
Receives StrategyFragments containing: strategy config, training metrics, stress results (gates, scores, per-variant performance), symbolic features.

**Processing**:
- Symbolic: Enrich with conservation laws, symmetries (from extractor or PySR).
- Causal: Double Machine Learning (DML) to estimate effects of hyperparameters/choices on outcomes (treatment = strategy feature, outcome = combined score or robustness).
- Knowledge Base: Update priors, causal graphs, and specialist performance history.

**Outputs**:
- Updated priors for agents (via MCP or challenge metadata).
- Specialist distillation candidates.
- Causal insights for roadmap/challenge design.
- Inputs to Symbolic Gauntlet.

**Future**: Integration with multi-physics composition and Foundation Operator (LPM with FiLM conditioning, evidential UQ).

See design notes for DML implementation sketch and data schemas.

---

## 10. Symbolic Layer

**Metadata Extraction**:
`SymbolicMetadataExtractor.extract(challenge_id, config) -> SymbolicMetadata` (rule-based Phase 0; ModelingToolkit upgrade planned).

**PySR Track**:
`PySRTrackRunner.run(trajectories, challenge_id, config) -> SymbolicRegressionResult`.
Graceful fallback if pysr not installed. Configurable parsimony, operators, iterations.

**Integration Points**:
- Attached to Challenge objects.
- Used in Landscape Agent.
- Planned: Auto loss weighting, Symbolic Gauntlet during distillation.

See `neurons/symbolic/` and docs/SYMBOLIC_LAYER_DESIGN.md.

---

## 11. Challenge Generation

```python
def generate_challenge(challenge_id: str, config: Optional[Dict] = None) -> Challenge:
    # Deterministic
    # Attaches symbolic_metadata via extractor
    # Includes stress_config and training/holdout references
```

Supports physics_class-specific stress configuration and future multi-physics definitions.

---

## 12. Phased Roadmap (Build-Level Deliverables)

**Phase 0**:
- Stress generators (procedural deep per class + Well) with determinism.
- StressEvaluator + full integration into HydrogenScorer and validator.
- Determinism utilities (seeding, setup functions, harness).
- MCP basics + testing loop.
- Symbolic skeleton (extractor + PySR runner).
- ChallengeWinnerTracker.
- generate_challenge() with symbolic attachment.

**Phase 1**:
- Abaqus ODB/.fil ingestion pipeline (parse_abaqus_odb, parse_abaqus_fil, CustomDataset).
- Expanded Landscape Agent (initial DML causal updates, symbolic enrichment).
- Deeper determinism in data loading/augmentation/training.
- Custom dataset + LoRA support in strategy schema.

**Phase 2**:
- preCICE integration for multi-physics (FSI/CHT/Thermo-elasticity).
- Specialist pipeline JSON schema and execution.
- Growing Specialist Bank + distillation.
- Variant expansion and reference generation (48 Tier-1 cases, etc.).

**Phase 3**:
- 3D turbulence bridge and 3D multi-physics.
- Advanced Landscape Agent compounding and outputs.
- Foundation Operator foundations (LPM, FiLM, UQ).

---

## 13. Current Implementation References

Key files:
- `neurons/stress/` (models, generators, evaluator)
- `neurons/scoring/hydrogen_scorer.py` (with stress integration)
- `neurons/validator.py` (full loop with determinism and MCP handling)
- `neurons/symbolic/` (models, extractor, pysr_runner)
- `neurons/utils/determinism.py`
- `neurons/challenge/generator.py`

See individual design docs in `docs/` for deeper supporting specifications.

---

*This specification is intended as a buildable reference. Implementations should match the interfaces, data models, and flows described above.*
