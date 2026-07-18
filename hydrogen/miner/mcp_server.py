"""MCP-style Server with persistent sessions + improved features.

Features:
- File-based persistent sessions
- Session metadata and expiration
- Better tool self-description
"""

import os
import json
import time
import uuid

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from hydrogen.miner.agent import AgenticMiner
from hydrogen.miner.client import MockHydrogenClient


app = FastAPI(
    title="Hydrogen Mining MCP Server",
    description="Advanced MCP-style server with persistent sessions.",
    version="0.5.0",
)

# ============================================================
# Persistent Session Storage (file-based)
# ============================================================

SESSION_DIR = "./sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

SESSION_TTL = 3600 * 24  # 24 hours


def _session_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"{session_id}.json")


def load_session(session_id: str) -> dict:
    path = _session_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)

    # Check expiration
    if time.time() - data.get("last_accessed", 0) > SESSION_TTL:
        os.remove(path)
        return None

    return data


def save_session(session_id: str, data: dict):
    data["last_accessed"] = time.time()
    path = _session_path(session_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_or_create_session(session_id: str = None) -> tuple:
    if session_id:
        existing = load_session(session_id)
        if existing:
            return session_id, existing

    new_id = str(uuid.uuid4())
    new_session = {
        "created_at": time.time(),
        "last_accessed": time.time(),
        "challenge_id": None,
        "best_strategy": None,
        "history": [],
        "metadata": {},
    }
    save_session(new_id, new_session)
    return new_id, new_session


# ============================================================
# Client
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
    session_id, _ = get_or_create_session()
    return CreateSessionResponse(session_id=session_id)


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, auth: bool = Depends(verify_api_key)):
    data = load_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return data


# ============================================================
# Tool Endpoints
# ============================================================

@app.get("/tools/list_challenges")
async def list_challenges(auth: bool = Depends(verify_api_key)):
    return await miner.get_challenges()


@app.post("/tools/get_priors")
async def get_priors(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    if session_id:
        sid, data = get_or_create_session(session_id)
        data["challenge_id"] = challenge_id
        save_session(sid, data)

    return await miner.get_priors(challenge_id)


@app.post("/tools/propose_strategy")
async def propose_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    base = payload.get("base_strategy")
    session_id = payload.get("session_id")

    strategy = await miner.propose_strategy(challenge_id, base_strategy=base)

    if session_id:
        sid, data = get_or_create_session(session_id)
        data["best_strategy"] = strategy
        save_session(sid, data)

    return strategy


@app.post("/tools/validate_strategy")
async def validate_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    quick = payload.get("quick", True)
    session_id = payload.get("session_id")

    result = await miner.validate_locally(strategy, challenge_id, quick=quick)

    if session_id:
        sid, data = get_or_create_session(session_id)
        data["history"].append({"action": "validate", "result": result})
        save_session(sid, data)

    return result


@app.post("/tools/submit_strategy")
async def submit_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    result = await miner.submit(strategy, challenge_id)

    if session_id:
        sid, data = get_or_create_session(session_id)
        data["history"].append({"action": "submit", "result": result})
        save_session(sid, data)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
