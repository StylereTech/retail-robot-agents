"""
FastAPI Backend — Retail Robot Agents Demo
Iterations 3, 6, 8, 12, 13: config validation, real health, preload cache, DEMO_DATA_MODE, WS limit
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Iteration 3: Startup config validation ────────────────────────────────────
REQUIRED_ENV = ["MONGODB_URI"]

def validate_config():
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        logger.error(f"FATAL: Missing required env vars: {missing}")
        sys.exit(1)
    for k in REQUIRED_ENV:
        logger.info(f"Config: {k} = ***SET*** ✓")

validate_config()

# ── Iteration 12: DEMO_DATA_MODE ──────────────────────────────────────────────
DEMO_DATA_MODE = os.environ.get("DEMO_DATA_MODE", "live")
logger.info(f"DEMO_DATA_MODE = {DEMO_DATA_MODE}")

# Import after config validation
from demo_runner import run_demo, fetch_luxury_inventory, DEMO_CUSTOMER

# ── Iteration 8: Inventory preload cache ──────────────────────────────────────
inventory_cache: list[dict] = []
cache_loaded_at: str = ""

app = FastAPI(title="Retail Robot Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    global inventory_cache, cache_loaded_at
    logger.info("Preloading inventory cache...")
    try:
        inventory_cache = fetch_luxury_inventory(100, mode=DEMO_DATA_MODE)
        cache_loaded_at = datetime.now(timezone.utc).isoformat()
        logger.info(f"✅ Preloaded {len(inventory_cache)} products | mode={DEMO_DATA_MODE}")
    except Exception as e:
        logger.warning(f"Preload failed, will use curated fallback: {e}")
        inventory_cache = []
    asyncio.create_task(refresh_cache_loop())


async def refresh_cache_loop():
    global inventory_cache, cache_loaded_at
    while True:
        await asyncio.sleep(1800)
        try:
            fresh = fetch_luxury_inventory(100, mode=DEMO_DATA_MODE)
            if fresh:
                inventory_cache = fresh
                cache_loaded_at = datetime.now(timezone.utc).isoformat()
                logger.info(f"Cache refreshed: {len(inventory_cache)} products")
        except Exception as e:
            logger.warning(f"Cache refresh failed: {e}")


# ── Iteration 13: Connection limit ───────────────────────────────────────────
MAX_CONNECTIONS = 10

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> bool:
        if len(self.active) >= MAX_CONNECTIONS:
            await ws.accept()
            await ws.close(code=1008, reason="Server at capacity")
            return False
        await ws.accept()
        self.active.append(ws)
        return True

    def disconnect(self, ws: WebSocket):
        self.active = [w for w in self.active if w != ws]

    async def send(self, ws: WebSocket, data: dict):
        try:
            await ws.send_text(json.dumps(data))
        except Exception:
            self.disconnect(ws)


manager = ConnectionManager()


# ── Iteration 6: Real dependency-aware health endpoint ───────────────────────
@app.get("/api/health")
async def health():
    mongo_ok = False
    try:
        from pymongo import MongoClient
        client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        mongo_ok = True
        client.close()
    except Exception as e:
        logger.warning(f"MongoDB health ping failed: {e}")

    status = "ok" if mongo_ok else "degraded"
    return JSONResponse({
        "status": status,
        "version": "1.0.0",
        "mongodb": mongo_ok,
        "data_mode": DEMO_DATA_MODE,
        "inventory_cached": len(inventory_cache),
        "connections_active": len(manager.active),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, status_code=200 if mongo_ok else 503)


@app.get("/api/inventory")
async def get_inventory():
    items = inventory_cache if inventory_cache else fetch_luxury_inventory(48, mode=DEMO_DATA_MODE)
    return {"items": items, "count": len(items), "mode": DEMO_DATA_MODE}


@app.websocket("/ws/demo")
async def demo_websocket(ws: WebSocket):
    connected = await manager.connect(ws)
    if not connected:
        return

    logger.info(f"WS connected | active={len(manager.active)}")
    try:
        data = await ws.receive_text()
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            payload = {}

        # Ignore ping messages
        if payload.get("type") == "ping":
            await ws.send_text(json.dumps({"type": "pong"}))
            # Keep listening
            data = await ws.receive_text()
            try:
                payload = json.loads(data)
            except Exception:
                payload = {}

        customer = payload.get("customer", DEMO_CUSTOMER)
        catalog = inventory_cache if inventory_cache else None

        async def emit(event: dict):
            await manager.send(ws, event)

        await run_demo(customer, emit, catalog=catalog)

    except WebSocketDisconnect:
        logger.info("WS client disconnected")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        try:
            await ws.send_text(json.dumps({
                "type": "error",
                "message": "Demo encountered an error — please retry",
                "data": {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
        except Exception:
            pass
    finally:
        manager.disconnect(ws)
        logger.info(f"WS disconnected | active={len(manager.active)}")
