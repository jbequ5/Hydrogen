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
