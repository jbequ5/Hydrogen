"""Improved MCP-style Server for Hydrogen.

This version is more structured and closer to a native MCP server pattern.
It uses FastAPI but is designed to be easy to migrate to a full MCP runtime later.
"""

import os

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from hydrogen.miner.agent import AgenticMiner
from hydrogen.miner.client import MockHydrogenClient


app = FastAPI(
    title="Hydrogen Mining MCP Server",
    description="Structured tools for agentic mining in Hydrogen.",
    version="0.3.0",
)

# ============================================================
# Client & Miner Initialization
# ============================================================

client = MockHydrogenClient()
miner = AgenticMiner(client)


def get_miner() -> AgenticMiner:
    return miner


def verify_api_key(x_api_key: str = Header(None)):
    api_key = os.getenv("HYDROGEN_API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# ============================================================
# Tool Endpoints (MCP-style)
# ============================================================

@app.get("/tools/list_challenges")
async def list_challenges(auth: bool = Depends(verify_api_key)):
    return await miner.get_challenges()


@app.post("/tools/get_priors")
async def get_priors(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    if not challenge_id:
        raise HTTPException(status_code=400, detail="challenge_id is required")
    return await miner.get_priors(challenge_id)


@app.post("/tools/propose_strategy")
async def propose_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    base = payload.get("base_strategy")
    return await miner.propose_strategy(challenge_id, base_strategy=base)


@app.post("/tools/validate_strategy")
async def validate_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    quick = payload.get("quick", True)
    return await miner.validate_locally(strategy, challenge_id, quick=quick)


@app.post("/tools/submit_strategy")
async def submit_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    return await miner.submit(strategy, challenge_id)


@app.post("/tools/get_recent_results")
async def get_recent_results(payload: dict, auth: bool = Depends(verify_api_key)):
    limit = payload.get("limit", 10)
    return await miner.get_recent_performance(limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
