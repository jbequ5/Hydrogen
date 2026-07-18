"""MCP-style Server with basic session support.

Sessions allow agents to maintain state across multiple tool calls
(e.g., current challenge, best strategy, history).
"""

import os
import uuid

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from hydrogen.miner.agent import AgenticMiner
from hydrogen.miner.client import MockHydrogenClient


app = FastAPI(
    title="Hydrogen Mining MCP Server (with Sessions)",
    description="Structured tools with basic session support for agentic mining.",
    version="0.4.0",
)

# ============================================================
# In-memory session store (simple for now)
# ============================================================

sessions = {}  # session_id -> context dict


def get_or_create_session(session_id: str = None) -> str:
    if session_id and session_id in sessions:
        return session_id
    new_id = str(uuid.uuid4())
    sessions[new_id] = {
        "challenge_id": None,
        "best_strategy": None,
        "history": [],
    }
    return new_id


# ============================================================
# Client & Miner
# ============================================================

client = MockHydrogenClient()
miner = AgenticMiner(client)


def verify_api_key(x_api_key: str = Header(None)):
    api_key = os.getenv("HYDROGEN_API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ============================================================
# Health
# ============================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# ============================================================
# Session Management
# ============================================================

class CreateSessionResponse(BaseModel):
    session_id: str


@app.post("/sessions/create", response_model=CreateSessionResponse)
async def create_session(auth: bool = Depends(verify_api_key)):
    session_id = get_or_create_session()
    return CreateSessionResponse(session_id=session_id)


# ============================================================
# Tool Endpoints (with optional session_id)
# ============================================================

@app.get("/tools/list_challenges")
async def list_challenges(
    session_id: str = None, auth: bool = Depends(verify_api_key)
):
    return await miner.get_challenges()


@app.post("/tools/get_priors")
async def get_priors(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    if session_id:
        get_or_create_session(session_id)
        sessions[session_id]["challenge_id"] = challenge_id

    return await miner.get_priors(challenge_id)


@app.post("/tools/propose_strategy")
async def propose_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    base = payload.get("base_strategy")
    session_id = payload.get("session_id")

    strategy = await miner.propose_strategy(challenge_id, base_strategy=base)

    if session_id:
        get_or_create_session(session_id)
        sessions[session_id]["best_strategy"] = strategy

    return strategy


@app.post("/tools/validate_strategy")
async def validate_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    quick = payload.get("quick", True)
    session_id = payload.get("session_id")

    result = await miner.validate_locally(strategy, challenge_id, quick=quick)

    if session_id:
        get_or_create_session(session_id)
        sessions[session_id]["history"].append({"action": "validate", "result": result})

    return result


@app.post("/tools/submit_strategy")
async def submit_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    result = await miner.submit(strategy, challenge_id)

    if session_id:
        get_or_create_session(session_id)
        sessions[session_id]["history"].append({"action": "submit", "result": result})

    return result


@app.post("/tools/get_recent_results")
async def get_recent_results(payload: dict, auth: bool = Depends(verify_api_key)):
    limit = payload.get("limit", 10)
    session_id = payload.get("session_id")

    results = await miner.get_recent_performance(limit=limit)

    if session_id:
        get_or_create_session(session_id)

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
