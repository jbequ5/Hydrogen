# Hydrogen Miner Docker Environment

Uses the new client abstraction and AgenticMiner for clean, maintainable focused runs.

## Focused Mode

```bash
CHALLENGE_ID=poisson_2d_v1 docker compose up miner
```

Supports `DRY_RUN`, `ITERATIONS`, and `SUBMIT_THRESHOLD` via environment variables.

## Architecture

- Uses `AgenticMiner` + `MockHydrogenClient` (easily swappable with real client later)
- Clean separation between client and agent logic

## Future

When a real `HydrogenClient` is available, it can be plugged in with minimal changes.
