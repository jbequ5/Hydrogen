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

if [ -z "$CHALLENGE_ID" ]; then
    python examples/run_agentic_miner.py
    exit 0
fi

echo "Focused Mode: $CHALLENGE_ID"
echo "  Dry Run    : $DRY_RUN"
echo "  Iterations : $ITERATIONS"
echo "  Threshold  : $SUBMIT_THRESHOLD"
echo ""

# Use the new AgenticMiner + client abstraction
python -c "
import asyncio
import os

from hydrogen.miner.agent import AgenticMiner
from hydrogen.miner.client import MockHydrogenClient

async def run_focused():
    client = MockHydrogenClient()
    miner = AgenticMiner(client)

    # Pass dry run flag
    miner._dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'

    result = await miner.run_iteration(
        challenge_id=os.environ['CHALLENGE_ID'],
        iterations=int(os.environ.get('ITERATIONS', '8'))
    )

    print('Focused run complete. Result:', result)

asyncio.run(run_focused())
"

echo ""
echo "Done."
echo "=============================================="
