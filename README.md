# Hydrogen

**Decentralized Physics-Informed Neural Operator Subnet on Bittensor (SN63)**

Hydrogen focuses on discovering high-quality training strategies for physics-respecting neural surrogates through decentralized, adversarial evaluation.

## Current Status (July 2026)

- Multi-objective scoring (Physics, Robustness, Accuracy)
- `ChallengeWinnerTracker` with exponential decay and participation dust
- Strategy storage via `StrategyStore` abstraction
- Standard Yuma Consensus emissions (hybrid bounty model planned but not active)

## Key Features

- **3 High-Level Objectives**: Physics Fidelity (45%), Robustness (30%), Accuracy (25%)
- Only submissions that beat the current best **combined score** on a challenge receive meaningful weight
- Per-challenge leader tracking with exponential decay
- Participation dust for recent miners
- Clean `StrategyStore` interface (local file implementation included)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jbequ5/Hydrogen.git
cd Hydrogen

# Install dependencies
pip install -r requirements.txt

# Run the validator (dry run first)
python neurons/validator.py --dry_run true
```

## Documentation

| Document                    | Description                                      |
|-----------------------------|--------------------------------------------------|
| `SPEC.md`                   | High-level architecture and current components   |
| `docs/EMISSIONS.md`         | Current emissions model (standard Yuma)          |
| `docs/VALIDATOR_GUIDE.md`   | How to run and understand the validator          |

## Architecture Highlights

- `HydrogenScorer`: Computes multi-objective scores
- `ChallengeWinnerTracker`: Minos-style per-challenge winner tracking with decay + dust
- `Validator`: Orchestrates scoring, tracking, and weight submission
- `StrategyStore`: Abstraction for retrieving/storing miner strategies

## Current Limitations

- Strategy retrieval is currently local-file based
- No hybrid bounty/treasury layer yet
- Single-validator focused

## Future Direction

- Hybrid emissions model (Breakthrough Bounties + Decaying Stipends)
- Platform-backed strategy store
- Stronger anti-capture protections
- Multi-validator support

## License

MIT License

## Contributing

Contributions are welcome. Please open an issue or pull request.
