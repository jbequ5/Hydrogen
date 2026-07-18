# Hydrogen Miner Docker Environment

Clean and powerful for agents.

## Focused Mode

```bash
CHALLENGE_ID=poisson_2d_v1 docker compose up miner
```

Includes:
- Challenge-specific priors (with system noise)
- Performance summary (start vs best score)
- The actual best strategy
- Intelligent recommendations

## Environment Variables

- `CHALLENGE_ID`
- `DRY_RUN`
- `ITERATIONS`
- `SUBMIT_THRESHOLD`

## Output

Structured JSON with performance metrics and recommended next actions.
