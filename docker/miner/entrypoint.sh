#!/bin/bash
set -e

echo "=============================================="
echo "   Hydrogen Miner Environment (v0.3)"
echo "=============================================="
echo ""

# Show configuration
echo "Configuration:"
echo "  Hotkey     : ${HYDROGEN_HOTKEY:-<not set>}"
echo "  Wallet     : ${HYDROGEN_WALLET:-<not set>}"
echo "  API Key    : ${HYDROGEN_API_KEY:-<not set>}"
echo "  Challenge  : ${CHALLENGE_ID:-<all challenges>}"
echo ""

# If a specific challenge is provided, run focused mode
if [ -n "$CHALLENGE_ID" ]; then
    echo "Focused mode enabled for challenge: $CHALLENGE_ID"
    echo "Loading priors and running internal testing loop..."
    echo ""
    
    # Run focused iteration on the chosen challenge
    python -c "
import asyncio
from hydrogen.miner.agent import AgenticMiner

async def run_focused():
    # Note: In production, replace MockClient with real HydrogenClient
    class MockClient:
        async def get_active_challenges(self):
            return ['${CHALLENGE_ID}']
        async def get_priors(self, challenge_id):
            return {'recommended_backbone': 'fno', 'loss_vector': {'pde_residual': 1.0}}
        async def validate_locally(self, strategy, challenge_id, quick=True):
            return {'estimated_score': 0.085, 'physics_gates_passed': True}
        async def submit(self, challenge_id, strategy):
            return {'status': 'submitted', 'rank': 3}

    client = MockClient()
    miner = AgenticMiner(client)
    result = await miner.run_iteration('${CHALLENGE_ID}', iterations=6)
    print('Focused run complete. Result:', result)

asyncio.run(run_focused())
"
else
    echo "No specific challenge set. Running multi-challenge example..."
    echo ""
    python examples/run_agentic_miner.py
fi

echo ""
echo "=============================================="
echo "Finished."
