#!/bin/bash
set -e

echo "=============================================="
echo "   Hydrogen Miner Environment"
echo "=============================================="
echo ""

CHALLENGE_ID=${CHALLENGE_ID:-}
DRY_RUN=${DRY_RUN:-false}
ITERATIONS=${ITERATIONS:-8}
SUBMIT_THRESHOLD=${SUBMIT_THRESHOLD:-0.075}
USE_REAL_CLIENT=${USE_REAL_CLIENT:-false}

if [ -z "$CHALLENGE_ID" ]; then
    python examples/run_agentic_miner.py
    exit 0
fi

echo "Focused Mode: $CHALLENGE_ID"
echo "  Dry Run         : $DRY_RUN"
echo "  Iterations      : $ITERATIONS"
echo "  Threshold       : $SUBMIT_THRESHOLD"
echo "  Use Real Client : $USE_REAL_CLIENT"
echo ""

python -c "
import asyncio
import os

from hydrogen.miner.agent import AgenticMiner

from hydrogen.miner.client import MockHydrogenClient
# from hydrogen.miner.real_client import RealHydrogenClient   # Uncomment when ready

async def run():
    if os.environ.get('USE_REAL_CLIENT', 'false').lower() == 'true':
        # client = RealHydrogenClient()  # When implemented
        print('Real client not available yet. Falling back to Mock client.')
        client = MockHydrogenClient()
    else:
        client = MockHydrogenClient()

    miner = AgenticMiner(client)
    miner._dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'

    result = await miner.run_iteration(
        challenge_id=os.environ['CHALLENGE_ID'],
        iterations=int(os.environ.get('ITERATIONS', '8'))
    )

    print('Run complete. Result:', result)

asyncio.run(run())
"

echo ""
echo "Done."
echo "=============================================="
