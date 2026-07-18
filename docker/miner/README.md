# Hydrogen Miner Docker Environment

This provides a clean, intelligent way to run both example and custom agentic miners.

## Quick Start

```bash
# Copy example config
cp docker/miner/.env.example .env

# Edit .env with your details
nano .env

# Run (defaults to multi-challenge mode)
docker compose up miner
```

## Focused Mode (Recommended for Most Users)

You can focus on **one specific challenge** by setting `CHALLENGE_ID`:

```bash
CHALLENGE_ID=poisson_2d_v1 docker compose up miner
```

In focused mode the container will:
- Load challenge-specific priors from the Landscape
- Run an internal testing/iteration loop
- Only submit when the estimated score looks good

This is the recommended way to work on one challenge deeply.

## Multi-Challenge Mode

If you don't set `CHALLENGE_ID`, it runs the built-in example that iterates over all active challenges.

```bash
docker compose up miner
```

## Configuration

Set these in your `.env` file or as environment variables:

```bash
HYDROGEN_HOTKEY=5F...          # Your hotkey
HYDROGEN_WALLET=default        # Wallet name
HYDROGEN_API_KEY=secret        # Optional (for MCP server)
CHALLENGE_ID=poisson_2d_v1     # Optional: focus on one challenge
```

## Running Custom Agents

```bash
docker compose run miner python my_custom_agent.py
```

Or mount a local file:

```bash
docker run -v $(pwd)/my_agent.py:/app/my_agent.py hydrogen-miner python my_agent.py
```

## Tips

- Always start from priors when possible (`get_priors`)
- Use local validation aggressively before submitting
- See `STRATEGY.md` for strategy writing guidance
