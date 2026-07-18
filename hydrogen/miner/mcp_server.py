"""MCP-style Server with Redis Sentinel + fallback support.

Supports high-availability Redis via Sentinel, with graceful fallback
to direct Redis or file-based storage.
"""

import os
import json
import time
import uuid

import asyncio
try:
    import redis.asyncio as aioredis
    from redis.asyncio.sentinel import RedisSentinel
except ImportError:
    aioredis = None
    RedisSentinel = None

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse

from hydrogen.miner.agent import AgenticMiner
from hydrogen.miner.client import MockHydrogenClient


app = FastAPI(
    title="Hydrogen Mining MCP Server",
    description="MCP-style server with Redis Sentinel high availability.",
    version="1.1.0",
)

# ============================================================
# Redis / Sentinel Configuration
# ============================================================

REDIS_URL = os.getenv("REDIS_URL")
REDIS_SENTINEL_HOSTS = os.getenv("REDIS_SENTINEL_HOSTS")  # e.g. "host1:26379,host2:26379"
SENTINEL_SERVICE_NAME = os.getenv("REDIS_SENTINEL_SERVICE", "mymaster")
SESSION_TTL_SECONDS = 86400  # 24 hours

redis_client = None

if aioredis:
    try:
        if REDIS_SENTINEL_HOSTS:
            # Redis Sentinel mode (High Availability)
            sentinel_hosts = [
                tuple(h.split(":")) for h in REDIS_SENTINEL_HOSTS.split(",")
            ]
            sentinel = RedisSentinel(
                sentinel_hosts,
                sentinel_kwargs={"password": os.getenv("REDIS_SENTINEL_PASSWORD")},
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            redis_client = sentinel.master_for(
                SENTINEL_SERVICE_NAME,
                socket_timeout=5,
                health_check_interval=30,
            )
        elif REDIS_URL:
            # Direct Redis mode
            redis_client = aioredis.from_url(
                REDIS_URL,
                decode_responses=True,
                max_connections=50,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
            )
    except Exception:
        redis_client = None

# File fallback
SESSION_DIR = "./sessions"
if not redis_client:
    os.makedirs(SESSION_DIR, exist_ok=True)


def _get_session_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"{session_id}.json")


async def _load_session(session_id: str) -> dict:
    if redis_client:
        data = await redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else None
    else:
        path = _get_session_path(session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return json.load(f)


async def _save_session(session_id: str, data: dict):
    data["last_accessed"] = time.time()
    if redis_client:
        await redis_client.setex(
            f"session:{session_id}",
            SESSION_TTL_SECONDS,
            json.dumps(data)
        )
    else:
        path = _get_session_path(session_id)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


async def get_or_create_session(session_id: str = None) -> tuple[str, dict]:
    if session_id:
        existing = await _load_session(session_id)
        if existing:
            return session_id, existing

    new_id = str(uuid.uuid4())
    new_data = {
        "created_at": time.time(),
        "last_accessed": time.time(),
        "challenge_id": None,
        "best_strategy": None,
        "history": [],
        "metadata": {},
    }
    await _save_session(new_id, new_data)
    return new_id, new_data


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
    if REDIS_SENTINEL_HOSTS:
        backend = "redis-sentinel"
    elif redis_client:
        backend = "redis"
    else:
        backend = "file"
    return {"status": "ok", "session_backend": backend}


# ============================================================
# Sessions
# ============================================================

@app.post("/sessions/create")
async def create_session(auth: bool = Depends(verify_api_key)):
    session_id, _ = await get_or_create_session()
    return {"session_id": session_id}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, auth: bool = Depends(verify_api_key)):
    data = await _load_session(session_id)
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

    sid, data = await get_or_create_session(session_id)
    data["challenge_id"] = challenge_id
    await _save_session(sid, data)

    return await miner.get_priors(challenge_id)


@app.post("/tools/propose_strategy")
async def propose_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    challenge_id = payload.get("challenge_id")
    base = payload.get("base_strategy")
    session_id = payload.get("session_id")

    strategy = await miner.propose_strategy(challenge_id, base_strategy=base)

    sid, data = await get_or_create_session(session_id)
    data["best_strategy"] = strategy
    await _save_session(sid, data)

    return strategy


@app.post("/tools/validate_strategy")
async def validate_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    quick = payload.get("quick", True)
    session_id = payload.get("session_id")

    result = await miner.validate_locally(strategy, challenge_id, quick=quick)

    sid, data = await get_or_create_session(session_id)
    data["history"].append({"action": "validate", "result": result})
    await _save_session(sid, data)

    return result


@app.post("/tools/submit_strategy")
async def submit_strategy(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    result = await miner.submit(strategy, challenge_id)

    sid, data = await get_or_create_session(session_id)
    data["history"].append({"action": "submit", "result": result})
    await _save_session(sid, data)

    return result


# ============================================================
# Streaming
# ============================================================

@app.post("/tools/stream_validation")
async def stream_validation(payload: dict, auth: bool = Depends(verify_api_key)):
    strategy = payload.get("strategy")
    challenge_id = payload.get("challenge_id")
    session_id = payload.get("session_id")

    RETRY_MS = 3000

    async def event_generator():
        yield f"retry: {RETRY_MS}\n\n"

        for i in range(1, 6):
            progress = i * 20
            yield f"data: {{\"progress\": {progress}, \"message\": \"Validating...\"}}\n\n"
            await asyncio.sleep(0.5)

        result = await miner.validate_locally(strategy, challenge_id)

        if session_id:
            sid, data = await get_or_create_session(session_id)
            data["history"].append({"action": "stream_validate", "result": result})
            await _save_session(sid, data)

        yield f"data: {json.dumps(result)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
