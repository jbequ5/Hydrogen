# Assessment: SPEC/ROADMAP Readiness for Frontier Coding Model

## Verdict: **Yes, but with 3 critical gaps** that need filling before a coding model can build autonomously.

---

## ✅ What's Sufficient (Ready to Code)

| Component | Spec Coverage | Coding Model Can Build? |
|-----------|---------------|------------------------|
| **Chain Pallet Logic** | Emission math, challenge management, scoring consensus, slashing conditions | ✅ Yes — math is explicit |
| **Validator Pipeline** | Deterministic Python pseudocode, Docker images, physics gates, scoring formula | ✅ Yes — algorithmic |
| **Miner CLI** | JSON schemas, submission rules, fee structure | ✅ Yes — straightforward |
| **Landscape Agent DML** | Daily causal update pseudocode, DML config, baseline proposal | ✅ Yes — algorithmic |
| **Specialist Distillation** | Weekly distillation pseudocode, loss function, regression test | ✅ Yes — algorithmic |
| **Challenge Generation** | Deterministic generation with Well mapping, procedural variants | ✅ Yes — algorithmic |
| **Physics Gates** | All formulas, thresholds, phase-gated targets, 3D gates | ✅ Yes — mathematical |
| **Scoring Formula** | Complete with log-space improvement, soft penalties, UQ bonus | ✅ Yes — mathematical |
| **Emission Mechanics** | Challenge budget cap, 40/30/20/10 split, novelty bonus, bounty accumulation | ✅ Yes — explicit math |
| **Agent API Schemas** | REST endpoints, request/response JSON, SDK interface | ✅ Yes — explicit contracts |
| **Specialist Gauntlet** | 8-step pipeline, 3-judge panel, grounding gate, decontamination | ✅ Yes — procedural |
| **Well Integration** | Per-problem mapping, sampling function | ✅ Yes — procedural |
| **Emission Math** | Challenge budget cap, 40/30/20/10, novelty bonus, bounty accumulation | ✅ Yes |

---

## ❌ Critical Gaps (Coding Model Cannot Build Autonomously)

### Gap 1: **Chain Pallet Implementation Details** (Substrate/Rust)

| Missing | Why It Blocks |
|---------|---------------|
| **Storage structures** | `Challenge`, `Submission`, `Score`, `EmissionBudget`, `SpecialistRegistry` storage maps not defined |
| **Extrinsic definitions** | `submit_strategy`, `submit_specialist_pipeline`, `validate`, `claim_rewards`, `propose_baseline` signatures not specified |
| **Event definitions** | `ChallengeCreated`, `SubmissionReceived`, `ScoreSubmitted`, `RewardsDistributed`, `SpecialistPromoted` |
| **Error types** | `InvalidSubmission`, `InsufficientFee`, `ChallengeNotActive`, `InvalidPhysicsGate` |
| **Weight setting logic** | How validator median scores → miner weights → `set_weights` call |
| **Epoch/challenge timing** | How challenge deadlines map to block numbers/epochs |
| **Treasury/multi-sig pallet integration** | Owner treasury, time-locked vesting, 3/5 multi-sig implementation |

**Impact**: Coding model can write Rust but will hallucinate storage keys, event names, and extrinsic signatures.

---

### Gap 2: **Validator Docker Image Specification** (Infrastructure)

| Missing | Why It Blocks |
|---------|---------------|
| **Dockerfile templates** | Base image, PhysicsNeMo install, NeuralOperator install, entrypoint script |
| **Entrypoint script** | `train.py`, `evaluate.py`, `stress_test.py` CLI interfaces |
| **Config injection** | How miner JSON → environment variables / config file / CLI args |
| **GPU/CPU resource limits** | Docker `--gpus`, `--memory`, `--cpus` per backbone |
| **Determinism enforcement** | `torch.manual_seed`, `numpy.random.seed`, `CUDA_DETERMINISTIC=1` |
| **Output serialization** | Standardized `ValidationResult` JSON output format |
| **Error handling** | OOM, timeout, NaN loss, checkpoint resume |
| **Model checkpointing** | When/where to save checkpoints for distillation |
| **Well data mounting** | How Well slices are mounted/accessed inside container |

**Impact**: Coding model can write Python but will produce non-reproducible, non-deterministic validator images.

---

### Gap 3: **Chain-API-Validator Integration Contracts** (Interfaces)

| Missing | Why It Blocks |
|---------|---------------|
| **Challenge metadata on-chain** | What fields stored on-chain vs. IPFS/off-chain |
| **Submission commitment scheme** | How miner commits to JSON before reveal (private-until-proven) |
| **Validator assignment** | How 3+ validators selected per challenge (random? stake-weighted?) |
| **Score submission window** | Exact block window for validators to submit scores |
| **Consensus failure handling** | What happens if <3 validators submit, or median fails |
| **Reward distribution extrinsic** | Who calls `distribute_rewards` (anyone? owner? automated?) |
| **Baseline update mechanism** | How Landscape's proposed baseline JSON gets on-chain |
| **Specialist promotion on-chain** | How team-side gauntlet result → on-chain SpecialistRegistry update |

**Impact**: Coding model will design mismatched interfaces between chain, API, and validator.

---

## 📋 What to Add: 3 Appendices for Coding Model Readiness

### Appendix A: Chain Pallet Specification (Substrate/Rust)
```rust
// Storage
#[pallet::storage]
pub type Challenges<T: Config> = StorageMap<_, Blake2_128Concat, ChallengeId, Challenge<T>>;

#[pallet::storage]
pub type Submissions<T: Config> = StorageDoubleMap<_, Blake2_128Concat, ChallengeId, Blake2_128Concat, MinerId, Submission<T>>;

#[pallet::storage]
pub type ValidatorScores<T: Config> = StorageDoubleMap<_, Blake2_128Concat, ChallengeId, Blake2_128Concat, ValidatorId, Score>;

// Extrinsics
#[pallet::call]
impl<T: Config> Pallet<T> {
    #[pallet::weight(10_000)]
    pub fn submit_strategy(origin, challenge_id: ChallengeId, strategy_json: Vec<u8>) -> DispatchResult

    #[pallet::weight(10_000)]
    pub fn submit_specialist_pipeline(origin, challenge_id: ChallengeId, pipeline_json: Vec<u8>) -> DispatchResult

    #[pallet::weight(10_000)]
    pub fn submit_score(origin, challenge_id: ChallengeId, scores: Vec<(MinerId, Score)>) -> DispatchResult

    #[pallet::weight(10_000)]
    pub fn propose_baseline(origin, problem_id: ProblemId, baseline_json: Vec<u8>) -> DispatchResult

    #[pallet::weight(10_000)]
    pub fn promote_specialist(origin, specialist_id: SpecialistId, onnx_hash: Vec<u8>) -> DispatchResult
}

// Events
#[pallet::event]
pub enum Event<T: Config> {
    ChallengeCreated { challenge_id: ChallengeId, problem_id: ProblemId },
    SubmissionReceived { challenge_id: ChallengeId, miner: T::AccountId },
    ScoreSubmitted { challenge_id: ChallengeId, validator: T::AccountId },
    RewardsDistributed { challenge_id: ChallengeId, rewards: Vec<(T::AccountId, Balance)> },
    BaselineUpdated { problem_id: ProblemId, baseline_hash: Vec<u8> },
    SpecialistPromoted { specialist_id: SpecialistId, problem_id: ProblemId },
}
```

---

### Appendix B: Validator Docker Specification

```dockerfile
# Dockerfile.template
FROM nvcr.io/nvidia/pytorch:24.09-py3

# System deps
RUN apt-get update && apt-get install -y \
    libopenmpi-dev openmpi-bin \
    git wget curl

# PhysicsNeMo + NeuralOperator
RUN pip install --no-cache-dir \
    physicsnemo==0.4.0 \
    neural-operator==0.3.0 \
    hydra-core \
    omegaconf

# Hydrogen validator code
COPY validator/ /workspace/validator/
WORKDIR /workspace/validator

# Entrypoint
ENTRYPOINT ["python", "entrypoint.py"]
```

```python
# entrypoint.py
import os, json, torch, numpy as np
from validator.train import train_backbone
from validator.eval import evaluate, run_stress_test
from validator.uq import evaluate_uq

def main():
    # Determinism
    seed = int(os.environ.get("HYDROGEN_SEED", "42"))
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Load inputs
    challenge_id = os.environ["CHALLENGE_ID"]
    submission_json = json.loads(os.environ["SUBMISSION_JSON"])
    challenge_data_path = os.environ["CHALLENGE_DATA_PATH"]
    
    # Load challenge metadata
    with open(f"{challenge_data_path}/metadata.json") as f:
        challenge = json.load(f)
    
    # Load data splits
    train_data = load_data(f"{challenge_data_path}/train")
    holdout_data = load_data(f"{challenge_data_path}/holdout")
    stress_data = load_data(f"{challenge_data_path}/stress")
    
    # Execute
    if "specialist_pipeline" in submission_json:
        model = execute_specialist_pipeline(submission_json, challenge, train_data)
    else:
        model = train_backbone(submission_json, train_data)
    
    # Evaluate
    E_baseline = load_baseline_error(challenge_id)
    E_submission = evaluate(model, holdout_data)
    improvement = math.log(E_baseline) - math.log(E_submission)
    
    # Stress test
    stress_result = run_stress_test(model, stress_data, challenge)
    
    # UQ
    uq_metrics = evaluate_uq(model, stress_data, submission_json.get("uq_config", {}))
    
    # Score
    if stress_result.hard_failure:
        score = 0.0
    else:
        base_score = max(0.0, improvement)
        soft_penalty = stress_result.soft_penalty
        uq_bonus = 0.05 if uq_metrics.calibrated else 0.0
        score = (base_score * soft_penalty) + uq_bonus
    
    # Output
    result = ValidationResult(
        score=score,
        improvement=improvement,
        stress_passed=not stress_result.hard_failure,
        uq_calibrated=uq_metrics.calibrated,
        physics_gates=stress_result.gates,
        stress_details=stress_result.details
    )
    
    # Write output
    with open("/workspace/output/result.json", "w") as f:
        json.dump(result.dict(), f)
```

---

### Appendix C: Chain-API-Validator Integration Contract

```yaml
# integration_contract.yaml

chain:
  challenge_metadata_onchain:
    - challenge_id: ChallengeId
    - problem_id: ProblemId
    - baseline_config_hash: Hash
    - stress_floors: PDESpecificFloors
    - emission_budget: Balance
    - submission_deadline: BlockNumber
    - status: Enum[Active, Scoring, Completed]
  
  submission_commitment:
    scheme: "commit-reveal"
    commit_phase_blocks: 100  # blocks to submit hash
    reveal_phase_blocks: 50   # blocks to reveal JSON
    commitment_hash: keccak256(json + nonce)
  
  validator_assignment:
    method: "stake_weighted_random"
    min_validators: 3
    max_validators: 7
    selection_block: challenge_start_block + 10
  
  scoring_window:
    start_block: submission_deadline_block
    end_block: submission_deadline_block + 200  # ~4 hours at 12s blocks
    min_validator_submissions: 3
  
  consensus:
    method: "median"
    max_deviation: 0.1
    audit_trigger: deviation > 0.15
  
  reward_distribution:
    trigger: "any_caller"  # anyone can call after scoring_window ends
    splitter: "challenge_pallet"
    novelty_bonus_pool: 0.05 * challenge_budget
  
  baseline_update:
    proposer: "owner_account"
    frequency: "daily"
    approval: "owner_signature"
  
  specialist_promotion:
    proposer: "owner_account"
    gauntlet_result_hash: Hash
    specialist_onnx_hash: Hash
    validity_domain: JSON

api:
  endpoints:
    GET /challenges:
      response: ChallengeList
    GET /challenges/{id}:
      response: ChallengeDetail
    GET /challenges/{id}/baseline:
      response: StrategyJSON
    GET /challenges/{id}/priors:
      response: PriorList
    GET /specialists:
      response: SpecialistList
    POST /submit:
      request: SubmitRequest
      response: SubmitResponse
    GET /submissions/{id}:
      response: ValidationResult
  
  authentication:
    method: "hotkey_signature"
    payload: "challenge_id + submission_json + nonce"
    header: "X-Hotkey-Signature"

validator:
  docker_image: "hydrogen/validator:{backbone}-v24.09"
  env_vars:
    CHALLENGE_ID: "string"
    SUBMISSION_JSON: "string"
    CHALLENGE_DATA_PATH: "/data/challenge"
    HYDROGEN_SEED: "int"
    SUBMISSION_TYPE: "strategy|specialist_pipeline"
  volumes:
    - "/host/data:/data:ro"
    - "/host/output:/workspace/output:rw"
  gpus: "all"
  memory: "16g"  # Phase 0-2; "48g" for Phase 3
  timeout: "7200"  # 2 hours max
  output: "/workspace/output/result.json"
  determinism:
    torch_seed: "HYDROGEN_SEED"
    numpy_seed: "HYDROGEN_SEED"
    cuda_deterministic: true
    cudnn_benchmark: false
```

---

