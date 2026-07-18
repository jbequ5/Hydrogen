# Hydrogen Miner Docker Environment

High-quality, agent-optimized experience.

## Focused Mode

```bash
CHALLENGE_ID=poisson_2d_v1 docker compose up miner
```

Features:
- Challenge-specific priors with system noise
- Realistic iteration with gain tracking
- Returns the actual best strategy
- Performance summary + intelligent recommendations

## Environment Variables

- `CHALLENGE_ID`
- `DRY_RUN`
- `ITERATIONS`
- `SUBMIT_THRESHOLD`

## Output

Clean JSON summary with gain from baseline, best strategy, and recommended next actions.
