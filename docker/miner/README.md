# Hydrogen Miner Docker Environment

Supports both mock and (future) real client modes.

## Focused Mode

```bash
CHALLENGE_ID=poisson_2d_v1 docker compose up miner
```

## Environment Variables

- `CHALLENGE_ID` — Focus on one challenge
- `DRY_RUN` — Safe testing
- `ITERATIONS` — Max cycles
- `SUBMIT_THRESHOLD` — Score threshold for submission
- `USE_REAL_CLIENT` — Set to `true` when real client is available (currently falls back to mock)

## Architecture

Uses the new client abstraction so swapping to a real `HydrogenClient` is straightforward.
