3 Appendices for Coding Model Readiness

Appendix A: Chain Pallet Specification (Substrate/Rust)

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
Appendix B: Validator Docker Specification

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
Appendix C: Chain-API-Validator Integration Contract

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
