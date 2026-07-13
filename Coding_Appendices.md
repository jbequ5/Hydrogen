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

---

# Appendix B: Validator Runtime Specification (Merged)

**Single source of truth for validator execution environment, determinism, and chain/API integration.**

---

## B.1 Docker Image Specification

### Base Image
```dockerfile
FROM nvcr.io/nvidia/pytorch:24.09-py3

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenmpi-dev openmpi-bin \
    git wget curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# PhysicsNeMo + NeuralOperator (pinned to spec versions)
RUN pip install --no-cache-dir \
    physicsnemo==0.4.0 \
    neural-operator==0.3.0 \
    hydra-core \
    omegaconf \
    pyyaml \
    boto3 \
    requests

# Hydrogen validator code
COPY validator/ /workspace/validator/
WORKDIR /workspace/validator

# Non-root user for security
RUN useradd -m -u 1000 validator && chown -R validator:validator /workspace
USER validator

ENTRYPOINT ["python", "entrypoint.py"]
```

### Build Tags (Per Backbone)
| Image Tag | Backbone | Size Estimate |
|-----------|----------|---------------|
| `hydrogen/validator:fno-v24.09` | FNO | ~12 GB |
| `hydrogen/validator:pino-v24.09` | PINO | ~12 GB |
| `hydrogen/validator:deeponet-v24.09` | DeepONet | ~12 GB |
| `hydrogen/validator:gno-v24.09` | GNO | ~13 GB |
| `hydrogen/validator:oformer-v24.09` | OFormer | ~13 GB |

**Build Command:**
```bash
docker build --target fno -t hydrogen/validator:fno-v24.09 .
docker build --target pino -t hydrogen/validator:pino-v24.09 .
# ... etc
```

---

## B.2 Entrypoint & Execution Interface

### Entrypoint Script (`entrypoint.py`)
```python
#!/usr/bin/env python3
"""
Validator Entrypoint
Environment variables control all behavior (no CLI args).
"""
import os, json, math, torch, numpy as np
import sys, traceback

# Determinism - MUST BE FIRST
seed = int(os.environ.get("HYDROGEN_SEED", "42"))
torch.manual_seed(seed)
np.random.seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
torch.use_deterministic_algorithms(True)

# Imports after determinism
from validator.train import train_backbone, execute_specialist_pipeline
from validator.eval import evaluate, run_stress_test
from validator.uq import evaluate_uq
from validator.io import load_challenge_data, load_baseline_error, save_result

def main():
    try:
        # Required environment variables
        challenge_id = os.environ["CHALLENGE_ID"]
        submission_json = json.loads(os.environ["SUBMISSION_JSON"])
        challenge_data_path = os.environ["CHALLENGE_DATA_PATH"]
        challenge_phase = int(os.environ.get("CHALLENGE_PHASE", "0"))
        
        # Load challenge metadata
        with open(f"{challenge_data_path}/metadata.json") as f:
            challenge = json.load(f)
        
        # Load data splits
        train_data, holdout_data, stress_data = load_challenge_data(challenge_data_path)
        
        # Parse submission
        submission = json.loads(os.environ["SUBMISSION_JSON"])
        
        # Execute
        if "specialist_pipeline" in submission:
            model = execute_specialist_pipeline(
                pipeline=submission["specialist_pipeline"],
                challenge={"phase": challenge_phase, **challenge},
                train_data=None,  # Specialists don't need training data
                seed=int(os.environ["HYDROGEN_SEED"])
            )
        else:
            # Load training data
            train_data, holdout_data, stress_data = load_challenge_data(challenge_data_path)
            
            # Handle custom data if present
            custom_data = submission.get("custom_data")
            if custom_data:
                custom_data = resolve_custom_data(custom_data, challenge_data_path)
            
            model = train_backbone(
                config=submission,
                train_data=train_data,
                custom_data=custom_data,
                seed=int(os.environ["HYDROGEN_SEED"])
            )
        
        # Evaluate on public holdout
        E_baseline = load_baseline_error(challenge_id)
        E_submission = evaluate(model, holdout_data, challenge_phase)
        improvement = math.log(E_baseline) - math.log(E_submission)
        
        # Hidden stress test + physics gates
        stress_result = run_stress_test(model, stress_data, challenge)
        
        # UQ calibration check
        uq_metrics = evaluate_uq(model, stress_data, submission.get("uq_config", {}))
        
        # Compute score
        if stress_result.hard_failure:
            score = 0.0
            reason = stress_result.failure_reason
        else:
            base_score = max(0.0, improvement)
            soft_penalty = stress_result.soft_penalty
            uq_bonus = uq_calibration_bonus(uq_metrics, challenge_phase)
            score = (base_score * soft_penalty) + uq_bonus
        
        # Build result
        result = {
            "score": score,
            "improvement": improvement,
            "stress_passed": not stress_result.hard_failure,
            "uq_calibrated": uq_metrics.calibrated,
            "physics_gates": stress_result.gates,
            "stress_details": stress_result.details,
            "uq_metrics": {
                "coverage": uq_metrics.coverage,
                "calibration_error": uq_metrics.calibration_error,
                "sharpness": uq_metrics.sharpness
            }
        }
        
        # Save result
        save_result("/workspace/output/result.json", result)
        print(json.dumps({"status": "success", "score": score}))
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        with open("/workspace/output/result.json", "w") as f:
            json.dump({"status": "error", "error": str(e)}, f)
        print(json.dumps({"status": "error", "error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## B.2 Environment Variables (Complete Contract)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CHALLENGE_ID` | Yes | Unique challenge identifier | `ns_2d_v1_0042` |
| `SUBMISSION_JSON` | Yes | Miner's full submission as JSON string | `{"backbone":"PINO",...}` |
| `CHALLENGE_DATA_PATH` | Yes | Path to mounted challenge data | `/data/challenge` |
| `CHALLENGE_PHASE` | Yes | Current subnet phase (0-3) | `0` |
| `HYDROGEN_SEED` | Yes | Deterministic seed for reproducibility | `42` |
| `SUBMISSION_JSON` | Yes | Full miner submission as JSON string | `{"backbone":"PINO",...}` |
| `SUBMISSION_TYPE` | No | `strategy` or `specialist_pipeline` | `strategy` |
| `CUSTOM_DATA_PATH` | No | Path to custom data if mounted | `/data/custom` |

---

## B.3 Docker Runtime Configuration

| Parameter | Phase 0-2 | Phase 3 (3D) |
|-----------|-----------|--------------|
| **GPU** | `--gpus all` (1 GPU) | `--gpus all` (1 GPU, 24GB+) |
| **Memory** | `--memory=16g` | `--memory=48g` |
| **Shared Memory** | `--shm-size=8g` | `--shm-size=16g` |
| **CPU** | `--cpus=8` | `--cpus=16` |
| **Timeout** | 7200s (2hr) | 14400s (4hr) |
| **Volumes** | `-v /host/data:/data:ro -v /host/output:/workspace/output:rw` | Same |
| **IPC** | `--ipc=host` | Same |
| **ULimits** | `--ulimit memlock=-1 --ulimit stack=67108864` | Same |

### Docker Compose Snippet (Local Dev)
```yaml
services:
  validator:
    image: hydrogen/validator:pino-v24.09
    environment:
      - CHALLENGE_ID=ns_2d_v1_0042
      - SUBMISSION_JSON=${SUBMISSION_JSON}
      - CHALLENGE_DATA_PATH=/data/challenge
      - CHALLENGE_PHASE=0
      - HYDROGEN_SEED=42
    volumes:
      - ./data:/data:ro
      - ./output:/workspace/output
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    shm_size: 8g
    mem_limit: 16g
    cpus: '8'
```

---

## B.4 Determinism Requirements (Enforced in Container)

| Setting | Value | Enforcement |
|---------|-------|-------------|
| `torch.manual_seed` | `HYDROGEN_SEED` | Entrypoint |
| `numpy.random.seed` | `HYDROGEN_SEED` | Entrypoint |
| `torch.cuda.manual_seed_all` | `HYDROGEN_SEED` | Entrypoint |
| `torch.backends.cudnn.deterministic` | `True` | Entrypoint |
| `torch.backends.cudnn.benchmark` | `False` | Entrypoint |
| `torch.use_deterministic_algorithms` | `True` | Entrypoint |
| `CUBLAS_WORKSPACE_CONFIG` | `:4096:8` | Dockerfile ENV |
| `PYTHONHASHSEED` | `HYDROGEN_SEED` | Dockerfile ENV |
| `OMP_NUM_THREADS` | `1` | Dockerfile ENV |
| `MKL_NUM_THREADS` | `1` | Dockerfile ENV |

**Validation**: Container must pass determinism test — same seed + same input = bitwise identical output.

---

## B.5 Input/Output Contract

### Input: Challenge Data Structure (Mounted at `/data/challenge`)
```
/data/challenge/
├── metadata.json          # Challenge metadata (see below)
├── train/
│   ├── inputs.npy         # Training inputs [N, ...]
│   └── targets.npy        # Training targets [N, ...]
├── holdout/
│   ├── inputs.npy         # Holdout inputs [M, ...]
│   └── targets.npy        # Holdout targets [M, ...]
├── stress/
│   ├── procedural/        # Procedural variants
│   │   ├── inputs.npy
│   │   └── targets.npy
│   └── well_slices/       # The Well dataset slices
│       ├── slice_001.npz
│       └── ...
└── baseline_error.json    # {"error": 0.0123, "phase": 0}
```

### `metadata.json`
```json
{
  "challenge_id": "ns_2d_v1_0042",
  "problem_id": 4,
  "problem_name": "navier_stokes_2d",
  "phase": 0,
  "physics_class": "incompressible_fluid",
  "dimension": 2,
  "resolution": [128, 128],
  "stress_floors": {
    "mass_conservation": 1e-3,
    "energy_dissipation": 1e-4,
    "boundary": 1e-3,
    "rollout_steps": 100,
    "uq_target": 0.90
  },
  "well_mapping": ["turbulence", "mhd"],
  "coupling_spec": null
}
```

### Output: `/workspace/output/result.json`
```json
{
  "status": "success",
  "score": 0.047,
  "improvement": 0.0123,
  "stress_passed": true,
  "uq_calibrated": true,
  "physics_gates": {
    "mass_conservation": {"passed": true, "value": 4.2e-4, "threshold": 1e-3},
    "energy_dissipation": {"passed": true, "value": 8.1e-5, "threshold": 1e-4},
    "boundary_satisfaction": {"passed": true, "value": 3.1e-4, "threshold": 1e-3},
    "rollout_stability": {"passed": true, "value": 0.005, "threshold": 0.01},
    "uq_calibration": {"passed": true, "value": 0.012, "threshold": 0.02}
  },
  "stress_details": {
    "procedural_passed": 45,
    "procedural_failed": 0,
    "well_slices_passed": 48,
    "well_slices_failed": 2,
    "worst_case_degradation": 0.18
  },
  "uq_metrics": {
    "coverage": 0.912,
    "calibration_error": 0.012,
    "sharpness": 0.045
  }
}
```

**Error Output:**
```json
{
  "status": "error",
  "error": "OOM during training",
  "traceback": "..."
}
```

---

## B.6 Determinism Validation Test

**Required CI test for every validator image build:**

```bash
#!/bin/bash
# determinism_test.sh
set -e

IMAGE=$1
CHALLENGE_ID="determinism_test"
SEED=42

# Run 1
docker run --rm --gpus all \
  -e CHALLENGE_ID=$CHALLENGE_ID \
  -e SUBMISSION_JSON='{"backbone":"PINO","physics_informed":true}' \
  -e CHALLENGE_DATA_PATH=/data \
  -e CHALLENGE_PHASE=0 \
  -e HYDROGEN_SEED=$SEED \
  -v $(pwd)/test_data:/data:ro \
  -v $(pwd)/output1:/workspace/output \
  $IMAGE

# Run 2
docker run --rm --gpus all \
  -e CHALLENGE_ID=$CHALLENGE_ID \
  -e SUBMISSION_JSON='{"backbone":"PINO","physics_informed":true}' \
  -e CHALLENGE_DATA_PATH=/data \
  -e CHALLENGE_PHASE=0 \
  -e HYDROGEN_SEED=$SEED \
  -v $(pwd)/test_data:/data:ro \
  -v $(pwd)/output2:/workspace/output \
  $IMAGE

# Compare outputs (must be bitwise identical)
diff output1/result.json output2/result.json
echo "✅ Determinism verified: bitwise identical outputs"
```

---

## B.7 Integration Contract (Chain ↔ API ↔ Validator)

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
    commit_phase_blocks: 100
    reveal_phase_blocks: 50
    commitment_hash: "keccak256(json + nonce)"
  
  validator_assignment:
    method: "stake_weighted_random"
    min_validators: 3
    max_validators: 7
    selection_block: "challenge_start_block + 10"
  
  scoring_window:
    start_block: "submission_deadline_block"
    end_block: "submission_deadline_block + 200"
    min_validator_submissions: 3
  
  consensus:
    method: "median"
    max_deviation: 0.1
    audit_trigger: 0.15
  
  reward_distribution:
    trigger: "any_caller"
    splitter: "challenge_pallet"
    novelty_bonus_pool: "0.05 * challenge_budget"
  
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
  memory: "16g"
  timeout: "7200"
  output: "/workspace/output/result.json"
  determinism:
    torch_seed: "HYDROGEN_SEED"
    numpy_seed: "HYDROGEN_SEED"
    cuda_deterministic: true
    cudnn_benchmark: false
```

---

## B.7 Determinism Validation (CI Gate)

**Required in CI pipeline for every validator image build:**

```yaml
# .github/workflows/validator-determinism.yml
name: Validator Determinism Test
on: [push, pull_request]
jobs:
  determinism:
    runs-on: [self-hosted, gpu, linux]
    steps:
      - uses: actions/checkout@v4
      - name: Build validator images
        run: ./scripts/build_validator_images.sh
      - name: Run determinism test
        run: ./scripts/determinism_test.sh hydrogen/validator:pino-v24.09
      - name: Upload result artifact
        uses: actions/upload-artifact@v4
        with:
          name: determinism-result
          path: determinism_report.json
```

---

*End of Appendix B: Validator Runtime Specification*

---

# Appendix C: Miner CLI Specification

**Complete CLI interface for miners to interact with Hydrogen subnet.**

---

## C.1 CLI Architecture

```bash
hydrogen-miner [GLOBAL_OPTIONS] <COMMAND> [COMMAND_OPTIONS]
```

**Global Options:**
| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--wallet.name` | `-w` | Yes | — | Wallet name (registered on Bittensor) |
| `--wallet.hotkey` | `-k` | Yes | — | Hotkey name (registered on Bittensor) |
| `--netuid` | `-n` | Yes | `107` | Subnet UID |
| `--subtensor.network` | `-s` | No | `finney` | Subtensor network (finney/test/local) |
| `--subtensor.chain_endpoint` | `-e` | No | `wss://entrypoint-finney.opentensor.ai:443` | Subtensor RPC endpoint |
| `--api.url` | `-a` | No | `https://api.hydrogen.subnet` | Hydrogen API base URL |
| `--config` | `-c` | No | `~/.hydrogen/miner.yaml` | Config file path |
| `--verbose` | `-v` | No | `false` | Verbose logging |
| `--dry-run` | `-d` | No | `false` | Simulate without submitting |

---

## C.2 Commands

### C.2.1 `hydrogen-miner submit` — Submit Strategy or Specialist Pipeline

```bash
hydrogen-miner submit --challenge-id <ID> --strategy <FILE> [OPTIONS]
hydrogen-miner submit --challenge-id <ID> --pipeline <FILE> [OPTIONS]
```

**Options:**
| Flag | Required | Description |
|------|----------|-------------|
| `--challenge-id` | Yes | Challenge ID to submit to |
| `--strategy` | Yes* | Path to Strategy JSON file (Phase 0-1) |
| `--pipeline` | Yes* | Path to Specialist Pipeline JSON file (Phase 2+) |
| `--custom-data` | No | Path to custom data file (Phase 1+) |
| `--fee` | No | Override default 0.1 TAO fee |
| `--nonce` | No | Custom nonce for commit-reveal |

*Exactly one of `--strategy` or `--pipeline` required.*

**Examples:**
```bash
# Submit strategy
hydrogen-miner submit --challenge-id ns_2d_v1_0042 --strategy my_strategy.json

# Submit specialist pipeline
hydrogen-miner submit --challenge-id fsi_2d_v1_0012 --pipeline my_pipeline.json

# With custom data
hydrogen-miner submit --challenge-id darcy_2d_0003 --strategy strategy.json --custom-data my_data.npz
```

**Output:**
```json
{
  "submission_id": "sub_abc123",
  "challenge_id": "ns_2d_v1_0042",
  "status": "accepted",
  "commit_tx_hash": "0xabc123...",
  "reveal_deadline_block": 1234567,
  "fee_paid": "0.1 TAO"
}
```

---

### C.2.2 `hydrogen-miner challenges` — List Active Challenges

```bash
hydrogen-miner challenges [OPTIONS]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--status` | Filter by status: `active`, `scoring`, `completed` |
| `--problem` | Filter by problem ID (1-7) |
| `--format` | Output format: `table`, `json`, `yaml` |
| `--watch` | Watch for new challenges (poll every 30s) |

**Output (table):**
```
┌──────────────────┬──────────────┬────────────┬──────────────┬────────────────────┬────────────┐
│ Challenge ID     │ Problem      │ Dimension  │ Status       │ Deadline (UTC)     │ Budget     │
├──────────────────┼──────────────┼────────────┼──────────────┼────────────────────┼────────────┤
│ ns_2d_v1_0042    │ Navier-Stokes│ 2D         │ active       │ 2026-07-15 20:00   │ 1240 TAO   │
│ darcy_3d_0012    │ Darcy 3D     │ 3D         │ active       │ 2026-07-15 22:00   │ 1240 TAO   │
│ thermo_el_0005   │ Thermo-elast │ 2D         │ scoring      │ 2026-07-15 18:00   │ 1240 TAO   │
└──────────────────┴──────────────┴────────────┴──────────────┴────────────────────┴────────────┘
```

---

### C.2.3 `hydrogen-miner baseline` — Get Current Baseline

```bash
hydrogen-miner baseline --challenge-id <ID> [OPTIONS]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--output` | Output file path (default: stdout) |
| `--format` | `json` or `yaml` |

**Output:**
```json
{
  "challenge_id": "ns_2d_v1_0042",
  "problem_id": 4,
  "baseline": {
    "backbone": "PINO",
    "resolution": [128, 128],
    "pino": {
      "loss_vector": {"pde_residual": 1.5, "conservation": 0.8, "boundary": 0.5, "symmetry": 0.3},
      "physics_loss_type": "pde_residual",
      "boundary_handling": "ghost_cells"
    },
    "optimizer": "AdamW",
    "learning_rate": 0.001,
    "scheduler": "CosineAnnealingLR",
    "batch_size": 32,
    "epochs": 150,
    "physics_informed": true,
    "curriculum_learning": {"enabled": true, "start_resolution": [64, 64], "end_resolution": [128, 128], "ramp_epochs": 50},
    "uq_config": {"method": "deep_ensemble", "num_members": 4, "calibration_target": 0.90}
  },
  "last_updated": "2026-07-14T14:30:00Z",
  "version": 42
}
```

---

### C.2.4 `hydrogen-miner priors` — Get Landscape Priors

```bash
hydrogen-miner priors --challenge-id <ID> [OPTIONS]
```

**Output:**
```json
{
  "challenge_id": "ns_2d_v1_0042",
  "priors": [
    {
      "parameter": "pino.loss_vector.pde_residual",
      "recommended_range": [1.2, 2.0],
      "causal_effect": "+0.015 improvement",
      "confidence": 0.92,
      "supporting_fragments": 87,
      "condition": "when physics_loss_type == 'pde_residual'"
    },
    {
      "parameter": "curriculum_learning.enabled",
      "recommended_range": [true],
      "causal_effect": "+0.008 improvement",
      "confidence": 0.78,
      "supporting_fragments": 45
    },
    {
      "parameter": "optimizer",
      "recommended_range": ["AdamW"],
      "causal_effect": "+0.003 vs Adam",
      "confidence": 0.65,
      "supporting_fragments": 23
    }
  ],
  "last_updated": "2026-07-14T14:30:00Z"
}
```

---

### C.2.5 `hydrogen-miner specialists` — List Available Specialists

```bash
hydrogen-miner specialists [OPTIONS]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--problem` | Filter by problem ID |
| `--phase` | Filter by phase compatibility |
| `--format` | `table`, `json`, `yaml` |

**Output (table):**
```
┌─────────────────────┬──────────────┬──────────────────────────────────────┬────────────┐
│ Specialist ID       │ Problem      │ Validity Domain                      │ Version    │
├─────────────────────┼──────────────┼──────────────────────────────────────┼────────────┤
│ ns_2d_v4            │ Navier-Stokes│ Re≤500, structured grid, 128²        │ v4         │
│ darcy_2d_v3         │ Darcy 2D     │ contrast≤10⁴, log-perm, structured   │ v3         │
│ elasticity_2d_v2    │ Elasticity   │ λ/μ≤100, mixed BC, 128²              │ v2         │
└─────────────────────┴──────────────┴──────────────────────────────────────┴────────────┘
```

---

### C.2.6 `hydrogen-miner submit-data` — Submit Custom Data (Phase 1+)

```bash
hydrogen-miner submit-data --challenge-id <ID> --file <PATH> [OPTIONS]
```

**Options:**
| Flag | Required | Description |
|------|----------|-------------|
| `--challenge-id` | Yes | Challenge ID |
| `--file` | Yes | Path to data file (.npz, .h5, .npz) |
| `--usage` | No | `augment`, `curriculum`, `label_only` (default: `augment`) |
| `--weight` | No | Mixing weight 0-1 (default: 0.25) |
| `--encrypt` | No | Encrypt with landscape public key |

**Output:**
```json
{
  "data_id": "data_abc123",
  "challenge_id": "darcy_2d_0003",
  "checksum": "sha256:abc123...",
  "size_bytes": 10485760,
  "status": "accepted",
  "royalty_eligible": true
}
```

---

### C.2.8 `hydrogen-miner validate` — Local Validation (Pre-Submit Check)

```bash
hydrogen-miner validate --challenge-id <ID> --strategy <FILE> [OPTIONS]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--local` | Run validation locally (requires GPU) |
| `--quick` | Quick validation (1 epoch, reduced data) |
| `--full` | Full validation (matches validator) |

**Output:**
```json
{
  "valid": true,
  "estimated_score": 0.035,
  "estimated_improvement": 0.012,
  "physics_gates_check": {
    "mass_conservation": "likely_pass",
    "energy_dissipation": "likely_pass",
    "uq_calibration": "likely_pass"
  },
  "warnings": [
    "learning_rate 0.01 may be unstable; suggested ≤ 0.005"
  ],
  "estimated_cost_tao": 0.08
}
```

---

### C.2.9 `hydrogen-miner rewards` — Check Rewards & History

```bash
hydrogen-miner rewards [OPTIONS]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--challenge` | Filter by challenge ID |
| `--days` | History window (default: 30) |
| `--format` | `table`, `json`, `csv` |

**Output (table):**
```
┌──────────────────┬────────┬────────────┬─────────────┬────────────┐
│ Challenge ID     │ Rank   │ Score      │ Improvement │ Reward     │
├──────────────────┼────────┼────────────┼─────────────┼────────────┤
│ ns_2d_v1_0042    │ 1      │ 0.047      │ +0.012      │ 496 TAO    │
│ darcy_2d_0003    │ 2      │ 0.031      │ +0.008      │ 372 TAO    │
│ burgers_0015     │ 4      │ 0.015      │ +0.003      │ 124 TAO    │
└──────────────────┴────────┴────────────┴─────────────┴────────────┘
Total: 992 TAO (30 days)
```

---

### C.2.9 `hydrogen-miner config` — Manage Configuration

```bash
hydrogen-miner config [get|set|show] [KEY] [VALUE]
```

**Examples:**
```bash
hydrogen-miner config show                           # Show all config
hydrogen-miner config get wallet.name                # Get single value
hydrogen-miner config set wallet.name my_wallet      # Set value
hydrogen-miner config set api.url https://api.myhydrogen.com  # Custom API
```

---

## C.3 Configuration File (`~/.hydrogen/miner.yaml`)

```yaml
wallet:
  name: "my_wallet"
  hotkey: "my_hotkey"
  path: "~/.bittensor/wallets"

network:
  netuid: 107
  subtensor:
    network: "finney"
    chain_endpoint: "wss://entrypoint-finney.opentensor.ai:443"

api:
  url: "https://api.hydrogen.subnet"
  timeout: 30

submission:
  default_fee: 0.1  # TAO
  auto_reveal: true
  commit_reveal: true

validation:
  local_enabled: true
  quick_mode_default: true

logging:
  level: "INFO"
  file: "~/.hydrogen/logs/miner.log"
  max_size_mb: 100
```

---

## C.4 Python SDK Integration (`hydrogen_miner` package)

```python
from hydrogen_miner import MinerClient, Strategy, SpecialistPipeline

client = MinerClient(
    wallet_name="my_wallet",
    hotkey="my_hotkey",
    netuid=107,
    network="finney"
)

# Get challenges
challenges = client.list_challenges(status="active")

# Get baseline + priors
baseline = client.get_baseline("ns_2d_v1_0042")
priors = client.get_priors("ns_2d_v1_0042")

# Generate strategy (your logic)
strategy = Strategy(
    backbone="PINO",
    resolution=[128, 128],
    pino={"loss_vector": {"pde_residual": 1.8, "conservation": 1.0}},
    optimizer="AdamW",
    learning_rate=0.001,
    # ... priors-informed values
)

# Local validation (optional)
local_result = client.validate_locally(strategy, "ns_2d_v1_0042", quick=True)
if local_result.valid:
    # Submit
    result = client.submit_strategy("ns_2d_v1_0042", strategy)
    print(f"Rank: {result.rank}, Score: {result.score}, Reward: {result.emission_reward}")

# Check rewards
rewards = client.get_rewards(days=30)
print(f"Total 30-day rewards: {sum(r.reward for r in rewards)} TAO")
```

---

*End of Appendix C: Miner CLI Specification*

---

# Appendix D: Dashboard & Indexer Specification

**GraphQL API, real-time subscriptions, and data models for the Hydrogen Dashboard & Indexer.**

---

## D.1 GraphQL Schema

```graphql
# schema.graphql

scalar DateTime
scalar JSON
scalar BigInt

type Query {
  # Challenge queries
  challenge(id: ID!): Challenge
  challenges(filter: ChallengeFilter, pagination: Pagination): ChallengeConnection!
  activeChallenges: [Challenge!]!
  
  # Submission queries
  submission(id: ID!): Submission
  submissions(filter: SubmissionFilter, pagination: Pagination): SubmissionConnection!
  minerSubmissions(minerHotkey: String!, pagination: Pagination): SubmissionConnection!
  
  # Miner queries
  miner(hotkey: String!): Miner
  miners(filter: MinerFilter, pagination: Pagination): MinerConnection!
  leaderboard(phase: Int, limit: Int): [MinerRank!]!
  
  # Specialist queries
  specialist(id: ID!): Specialist
  specialists(filter: SpecialistFilter, pagination: Pagination): SpecialistConnection!
  specialistBank(problemId: Int): [Specialist!]!
  
  # Landscape queries
  causalGraph(problemId: Int, depth: Int): CausalGraph
  priors(challengeId: ID!): [Prior!]!
  baseline(challengeId: ID!): Baseline
  
  # Network stats
  networkStats: NetworkStats!
  emissionInfo: EmissionInfo!
}

type Mutation {
  # Miner mutations (called via API, signed by hotkey)
  submitStrategy(input: SubmitStrategyInput!): SubmissionResult!
  submitSpecialistPipeline(input: SubmitSpecialistPipelineInput!): SubmissionResult!
  submitCustomData(input: SubmitCustomDataInput!): CustomDataResult!
  
  # Validator mutations (called by validator hotkeys)
  submitScore(input: SubmitScoreInput!): ScoreResult!
  
  # Owner mutations (owner only)
  proposeBaseline(input: ProposeBaselineInput!): BaselineResult!
  promoteSpecialist(input: PromoteSpecialistInput!): SpecialistResult!
}

type Subscription {
  # Real-time updates
  challengeUpdates: ChallengeUpdate!
  submissionUpdates(minerHotkey: String): SubmissionUpdate!
  scoreUpdates(challengeId: ID!): ScoreUpdate!
  leaderboardUpdates: LeaderboardUpdate!
  specialistUpdates: SpecialistUpdate!
}

# ============================================================
# Core Types
# ============================================================

type Challenge {
  id: ID!
  problemId: Int!
  problemName: String!
  dimension: String!
  physicsClass: String!
  phase: Int!
  status: ChallengeStatus!
  resolution: String!
  emissionBudget: BigInt!
  submissionDeadline: DateTime!
  scoringDeadline: DateTime!
  baselineConfig: JSON!
  stressFloors: StressFloors!
  wellMapping: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  trainSamples: Int!
  holdoutSamples: Int!
  stressSamples: Int!
}

enum ChallengeStatus {
  ACTIVE
  SCORING
  COMPLETED
  ARCHIVED
}

type StressFloors {
  massConservation: Float!
  energyDissipation: Float!
  boundarySatisfaction: Float!
  rolloutSteps: Int!
  uqTarget: Float!
}

type Submission {
  id: ID!
  challenge: Challenge!
  miner: Miner!
  type: SubmissionType!
  strategyJson: JSON
  specialistPipeline: JSON
  customDataId: ID
  status: SubmissionStatus!
  submittedAt: DateTime!
  revealedAt: DateTime
  score: Float
  improvement: Float
  noveltyBonus: Float
  emissionReward: BigInt
  rank: Int
  physicsGates: PhysicsGateResults!
  stressDetails: StressDetails!
  causalInsights: [CausalInsight!]!
  validatorConsensus: ConsensusInfo!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum SubmissionType {
  STRATEGY
  SPECIALIST_PIPELINE
}

enum SubmissionStatus {
  COMMITTED
  REVEALED
  VALIDATING
  SCORED
  REWARDED
  REJECTED
}

type PhysicsGateResults {
  massConservation: GateResult!
  energyDissipation: GateResult!
  boundarySatisfaction: GateResult!
  rolloutStability: GateResult!
  uqCalibration: GateResult!
}

type GateResult {
  passed: Boolean!
  value: Float!
  threshold: Float!
  unit: String
}

type StressDetails {
  proceduralPassed: Int!
  proceduralFailed: Int!
  wellSlicesPassed: Int!
  wellSlicesFailed: Int!
  worstCaseDegradation: Float!
  gateResults: [GateResult!]!
}

type Miner {
  hotkey: String!
  coldkey: String
  uid: Int
  stake: BigInt
  totalRewards: BigInt!
  totalSubmissions: Int!
  successfulSubmissions: Int!
  winRate: Float!
  avgScore: Float!
  avgNoveltyBonus: Float!
  firstSubmissionAt: DateTime
  lastSubmissionAt: DateTime
  isActive: Boolean!
  registeredAt: DateTime!
}

type MinerRank {
  hotkey: String!
  rank: Int!
  score: Float!
  totalRewards: BigInt!
  challengesWon: Int!
  challengesParticipated: Int!
  avgNoveltyBonus: Float!
}

type Specialist {
  id: ID!
  problemId: Int!
  problemName: String!
  version: Int!
  onnxModelHash: String!
  validityDomain: ValidityDomain!
  stressTestResults: StressTestResults!
  metrics7d: Metrics7D!
  license: LicenseType!
  provenance: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  downloadUrl: String!
  downloadCount: Int!
  revenueGenerated: BigInt!
}

type ValidityDomain {
  parameters: JSON!
  constraints: [String!]!
  knownFailures: [String!]!
  recommendedUseCases: [String!]!
}

type StressTestResults {
  massConservation: Boolean!
  energyDissipation: Boolean!
  boundarySatisfaction: Boolean!
  rolloutStability: Boolean!
  uqCalibration: Boolean!
  spectralFidelity: Boolean
  couplingConsistency: Boolean
  addedMassTensor: Boolean
  nuDistribution: Boolean
}

type Metrics7D {
  fidelity: Float!
  accuracy: Float!
  efficiency: Float!
  robustness: Float!
  generalization: Float!
  interpretability: Float!
  usability: Float!
}

enum LicenseType {
  AGPL_3_0
  COMMERCIAL
  DUAL
}

type Prior {
  parameter: String!
  recommendedRange: JSON!
  causalEffect: String!
  confidence: Float!
  supportingFragments: Int!
  condition: String
  lastUpdated: DateTime!
}

type Baseline {
  challengeId: ID!
  problemId: Int!
  config: JSON!
  version: Int!
  lastUpdated: DateTime!
  proposedBy: String!
  approvedAt: DateTime!
}

type CausalGraph {
  nodes: [CausalNode!]!
  edges: [CausalEdge!]!
}

type CausalNode {
  id: ID!
  parameter: String!
  value: Float!
  ate: Float!
  confidence: Float!
  fragmentCount: Int!
}

type CausalEdge {
  from: ID!
  to: ID!
  interactionEffect: Float!
  confidence: Float!
}

type NetworkStats {
  totalMiners: Int!
  activeMiners24h: Int!
  activeValidators: Int!
  activeChallenges: Int!
  totalSubmissions24h: Int!
  avgScore24h: Float!
  totalEmissions24h: BigInt!
  specialistCount: Int!
  compositionWinRate: Float!
}

type EmissionInfo {
  totalEmission: BigInt!
  challengeBudget: BigInt!
  activeChallenges: Int!
  minerShare: Float!
  validatorShare: Float!
  ownerShare: Float!
  noveltyBonusPool: BigInt!
}

# ============================================================
# Input Types
# ============================================================

input ChallengeFilter {
  problemId: Int
  phase: Int
  status: ChallengeStatus
  dimension: String
}

input SubmissionFilter {
  challengeId: ID
  minerHotkey: String
  type: SubmissionType
  status: SubmissionStatus
  dateFrom: DateTime
  dateTo: DateTime
  minScore: Float
  maxScore: Float
}

input MinerFilter {
  isActive: Boolean
  minStake: BigInt
  minRewards: BigInt
}

input SpecialistFilter {
  problemId: Int
  license: LicenseType
  minFidelity: Float
}

input Pagination {
  first: Int
  after: String
  last: Int
  before: String
}

input SubmitStrategyInput {
  challengeId: ID!
  strategyJson: JSON!
  nonce: String!
  signature: String!
}

input SubmitSpecialistPipelineInput {
  challengeId: ID!
  pipelineJson: JSON!
  nonce: String!
  signature: String!
}

input SubmitCustomDataInput {
  challengeId: ID!
  dataUri: String!
  checksum: String!
  usage: String!
  weight: Float!
  encryption: EncryptionInput
}

input SubmitScoreInput {
  challengeId: ID!
  scores: [ValidatorScoreInput!]!
  signature: String!
}

input ValidatorScoreInput {
  minerHotkey: String!
  score: Float!
  improvement: Float!
  stressPassed: Boolean!
  uqCalibrated: Boolean!
  physicsGates: JSON!
  stressDetails: JSON!
}

input ProposeBaselineInput {
  problemId: Int!
  baselineJson: JSON!
  signature: String!
}

input PromoteSpecialistInput {
  specialistId: ID!
  gauntletResultHash: String!
  onnxModelHash: String!
  validityDomain: JSON!
  signature: String!
}

input SubmitCustomDataInput {
  challengeId: ID!
  dataUri: String!
  checksum: String!
  usage: String!
  weight: Float!
  encryption: EncryptionInput
}

input EncryptionInput {
  algorithm: String!
  keyId: String!
}

# ============================================================
# Connection Types (Relay-style pagination)
# ============================================================

type ChallengeConnection {
  edges: [ChallengeEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type ChallengeEdge {
  node: Challenge!
  cursor: String!
}

type SubmissionConnection {
  edges: [SubmissionEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type SubmissionEdge {
  node: Submission!
  cursor: String!
}

type MinerConnection {
  edges: [MinerEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type MinerEdge {
  node: Miner!
  cursor: String!
}

type SpecialistConnection {
  edges: [SpecialistEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type SpecialistEdge {
  node: Specialist!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# ============================================================
# Subscription Payloads
# ============================================================

type ChallengeUpdate {
  event: ChallengeEventType!
  challenge: Challenge!
  timestamp: DateTime!
}

enum ChallengeEventType {
  CREATED
  STATUS_CHANGED
  BASELINE_UPDATED
  COMPLETED
}

type SubmissionUpdate {
  event: SubmissionEventType!
  submission: Submission!
  timestamp: DateTime!
}

enum SubmissionEventType {
  SUBMITTED
  REVEALED
  SCORED
  REWARDED
  REJECTED
}

type ScoreUpdate {
  challengeId: ID!
  minerHotkey: String!
  score: Float!
  rank: Int!
  timestamp: DateTime!
}

type LeaderboardUpdate {
  phase: Int!
  rankings: [MinerRank!]!
  timestamp: DateTime!
}

type SpecialistUpdate {
  event: SpecialistEventType!
  specialist: Specialist!
  timestamp: DateTime!
}

enum SpecialistEventType {
  CREATED
  UPDATED
  PROMOTED
  DEPRECATED
}
```

---

## D.2 REST API Endpoints (Complementary to GraphQL)

```yaml
# REST endpoints for simple queries and webhooks

GET  /api/v1/challenges                    # List challenges with filters
GET  /api/v1/challenges/{id}               # Challenge details
GET  /api/v1/challenges/{id}/baseline      # Current baseline JSON
GET  /api/v1/challenges/{id}/priors        # Landscape priors (DML effects)
GET  /api/v1/challenges/{id}/submissions   # Submissions for challenge
GET  /api/v1/challenges/{id}/leaderboard   # Challenge leaderboard

GET  /api/v1/miners/{hotkey}               # Miner profile
GET  /api/v1/miners/{hotkey}/submissions   # Miner's submissions
GET  /api/v1/miners/{hotkey}/rewards       # Miner's rewards history

GET  /api/v1/specialists                   # List specialists
GET  /api/v1/specialists/{id}              # Specialist details
GET  /api/v1/specialists/{id}/download     # Download ONNX model

GET  /api/v1/landscape/priors/{challengeId} # Causal priors for challenge
GET  /api/v1/landscape/baseline/{challengeId} # Current baseline
GET  /api/v1/landscape/graph/{problemId}   # Causal graph for problem

GET  /api/v1/network/stats                 # Network statistics
GET  /api/v1/network/emissions             # Emission info

POST /api/v1/submit                        # Submit strategy/pipeline
POST /api/v1/webhooks/validator-score      # Validator webhook for scores

GET  /api/v1/health                        # Health check
GET  /api/v1/version                       # Version info
```

---

## D.3 Indexer Architecture

```yaml
# indexer.yaml

indexer:
  name: "hydrogen-indexer"
  version: "1.0.0"
  
  blockchain:
    network: "finney"
    ws_endpoint: "wss://entrypoint-finney.opentensor.ai:443"
    netuid: 107
    start_block: 1000000  # Subnet registration block
  
  database:
    type: "postgresql"
    host: "${DB_HOST}"
    port: 5432
    database: "hydrogen_indexer"
    user: "${DB_USER}"
    password: "${DB_PASSWORD}"
    pool_size: 20
    max_overflow: 10
  
  redis:
    host: "${REDIS_HOST}"
    port: 6379
    db: 0
    password: "${REDIS_PASSWORD}"
  
  sync:
    batch_size: 100
    block_interval: 12  # seconds
    confirmation_depth: 3
    retry_attempts: 5
    retry_delay: 5
  
  processing:
    workers: 4
    batch_size: 50
    queue_size: 10000
    dead_letter_queue: "hydrogen_dlq"
  
  graphql:
    host: "0.0.0.0"
    port: 4000
    playground: true
    introspection: true
    complexity_limit: 1000
    depth_limit: 10
  
  rest_api:
    host: "0.0.0.0"
    port: 8000
    cors_origins:
      - "https://dashboard.hydrogen.subnet"
      - "https://app.hydrogen.subnet"
    rate_limit:
      requests_per_minute: 120
      burst: 20
  
  websocket:
    host: "0.0.0.0"
    port: 4001
    ping_interval: 30
    ping_timeout: 10
  
  monitoring:
    prometheus_port: 9090
    health_check_port: 8080
    log_level: "INFO"
    log_format: "json"
```

---

## D.4 Database Schema (PostgreSQL)

```sql
-- schema.sql

-- Core tables
CREATE TABLE challenges (
    id VARCHAR(64) PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    problem_name VARCHAR(100) NOT NULL,
    dimension VARCHAR(20) NOT NULL,
    physics_class VARCHAR(100) NOT NULL,
    phase INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    resolution VARCHAR(50),
    emission_budget NUMERIC(78, 0) NOT NULL,
    submission_deadline TIMESTAMPTZ NOT NULL,
    scoring_deadline TIMESTAMPTZ NOT NULL,
    baseline_config JSONB NOT NULL,
    stress_floors JSONB NOT NULL,
    well_mapping JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    train_samples INTEGER,
    holdout_samples INTEGER,
    stress_samples INTEGER
);

CREATE INDEX idx_challenges_status ON challenges(status);
CREATE INDEX idx_challenges_problem_phase ON challenges(problem_id, phase);

CREATE TABLE submissions (
    id VARCHAR(64) PRIMARY KEY,
    challenge_id VARCHAR(64) REFERENCES challenges(id),
    miner_hotkey VARCHAR(128) NOT NULL,
    type VARCHAR(20) NOT NULL,
    strategy_json JSONB,
    specialist_pipeline JSONB,
    custom_data_id VARCHAR(64),
    status VARCHAR(20) NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL,
    revealed_at TIMESTAMPTZ,
    score NUMERIC(10, 6),
    improvement NUMERIC(10, 6),
    novelty_bonus NUMERIC(10, 6),
    emission_reward NUMERIC(78, 0),
    rank INTEGER,
    physics_gates JSONB,
    stress_details JSONB,
    causal_insights JSONB,
    validator_consensus JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_submissions_challenge ON submissions(challenge_id);
CREATE INDEX idx_submissions_miner ON submissions(miner_hotkey);
CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_score ON submissions(score DESC);

CREATE TABLE miners (
    hotkey VARCHAR(128) PRIMARY KEY,
    coldkey VARCHAR(128),
    uid INTEGER,
    stake NUMERIC(78, 0),
    total_rewards NUMERIC(78, 0) DEFAULT 0,
    total_submissions INTEGER DEFAULT 0,
    successful_submissions INTEGER DEFAULT 0,
    win_rate NUMERIC(5, 4) DEFAULT 0,
    avg_score NUMERIC(10, 6) DEFAULT 0,
    avg_novelty_bonus NUMERIC(10, 6) DEFAULT 0,
    first_submission_at TIMESTAMPTZ,
    last_submission_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE specialists (
    id VARCHAR(64) PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    problem_name VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    onnx_model_hash VARCHAR(64) NOT NULL,
    validity_domain JSONB NOT NULL,
    stress_test_results JSONB NOT NULL,
    metrics_7d JSONB,
    license VARCHAR(20) NOT NULL,
    provenance JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    download_url VARCHAR(512),
    download_count INTEGER DEFAULT 0,
    revenue_generated NUMERIC(78, 0) DEFAULT 0
);

CREATE INDEX idx_specialists_problem ON specialists(problem_id);
CREATE INDEX idx_specialists_version ON specialists(version);

CREATE TABLE strategy_fragments (
    id VARCHAR(64) PRIMARY KEY,
    miner_uid INTEGER NOT NULL,
    challenge_id VARCHAR(64) REFERENCES challenges(id),
    problem_id INTEGER NOT NULL,
    config_json JSONB NOT NULL,
    improvement NUMERIC(10, 6) NOT NULL,
    stress_passed BOOLEAN NOT NULL,
    uq_metrics JSONB,
    score NUMERIC(10, 6),
    timestamp TIMESTAMPTZ NOT NULL,
    causal_parents TEXT[],
    param_values JSONB
);

CREATE INDEX idx_fragments_problem ON strategy_fragments(problem_id);
CREATE INDEX idx_fragments_challenge ON strategy_fragments(challenge_id);
CREATE INDEX idx_fragments_improvement ON strategy_fragments(improvement DESC);

CREATE TABLE baselines (
    problem_id INTEGER PRIMARY KEY,
    config JSONB NOT NULL,
    version INTEGER NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    proposed_by VARCHAR(128),
    approved_at TIMESTAMPTZ
);

CREATE TABLE causal_edges (
    id BIGSERIAL PRIMARY KEY,
    from_fragment VARCHAR(64) NOT NULL,
    to_fragment VARCHAR(64) NOT NULL,
    interaction_effect NUMERIC(10, 6),
    confidence NUMERIC(5, 4),
    problem_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_causal_edges_problem ON causal_edges(problem_id);

-- Views for common queries
CREATE VIEW miner_stats AS
SELECT 
    m.hotkey,
    m.total_rewards,
    m.total_submissions,
    m.successful_submissions,
    CASE WHEN m.total_submissions > 0 
        THEN m.successful_submissions::numeric / m.total_submissions 
        ELSE 0 END as win_rate,
    m.avg_score,
    m.avg_novelty_bonus,
    MAX(s.submitted_at) as last_submission_at
FROM miners m
LEFT JOIN submissions s ON m.hotkey = s.miner_hotkey
GROUP BY m.hotkey, m.total_rewards, m.total_submissions, m.successful_submissions, m.avg_score, m.avg_novelty_bonus;

CREATE VIEW challenge_stats AS
SELECT 
    c.id,
    c.problem_id,
    c.status,
    COUNT(s.id) as total_submissions,
    COUNT(DISTINCT s.miner_hotkey) as unique_miners,
    MAX(s.score) as best_score,
    AVG(s.score) as avg_score,
    MAX(s.improvement) as best_improvement
FROM challenges c
LEFT JOIN submissions s ON c.id = s.challenge_id
GROUP BY c.id, c.problem_id, c.status;
```

---

## D.5 Real-time Subscriptions (GraphQL over WebSocket)

```typescript
// subscriptions.ts - Client-side subscription handlers

// Challenge updates
subscription ChallengeUpdates {
  challengeUpdates {
    event
    challenge {
      id
      status
      submissionDeadline
      emissionBudget
    }
    timestamp
  }
}

// Miner's submission updates
subscription MySubmissions($hotkey: String!) {
  submissionUpdates(minerHotkey: $hotkey) {
    event
    submission {
      id
      challenge { id problemName }
      status
      score
      rank
      emissionReward
    }
    timestamp
  }
}

// Live leaderboard
subscription Leaderboard($phase: Int!) {
  leaderboardUpdates(phase: $phase) {
    phase
    rankings {
      hotkey
      rank
      score
      totalRewards
    }
    timestamp
  }
}

// Challenge scoring updates
subscription ChallengeScores($challengeId: ID!) {
  scoreUpdates(challengeId: $challengeId) {
    challengeId
    minerHotkey
    score
    rank
    timestamp
  }
}

// Specialist bank updates
subscription SpecialistUpdates {
  specialistUpdates {
    event
    specialist {
      id
      problemName
      version
      validityDomain
      metrics7d {
        fidelity
        accuracy
      }
    }
    timestamp
  }
}
```

---

## D.6 Webhook Endpoints

```yaml
# Webhook endpoints for external integrations

POST /webhooks/validator-score
  # Called by validator after scoring
  # Payload: { challengeId, minerHotkey, score, improvement, stressPassed, uqCalibrated, physicsGates, stressDetails }
  # Response: { accepted: true, scoreId: "..." }

POST /webhooks/rewards-distributed
  # Called after rewards distributed
  # Payload: { challengeId, rewards: [{ minerHotkey, amount, rank }] }

POST /webhooks/specialist-promoted
  # Called when specialist promoted
  # Payload: { specialistId, problemId, version, validityDomain, onnxHash }

POST /webhooks/baseline-updated
  # Called when baseline updated
  # Payload: { problemId, version, baselineHash, proposedBy }
```

---

*End of Appendix D: Dashboard & Indexer Specification*
