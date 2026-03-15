"""
FastAPI Backend — Retail Robot Agents Demo
"""
from __future__ import annotations
import sys
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, '/tmp/retail-robot-agents/src')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from demo_runner import run_demo, fetch_luxury_inventory, DEMO_CUSTOMER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Retail Robot Agents Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Active WebSocket connections ─────────────────────────────────────────────
active_connections: list[WebSocket] = []
demo_running = False


async def broadcast_to_all(event: dict) -> None:
    """Send event to all active WebSocket connections."""
    message = json.dumps(event)
    dead = []
    for ws in active_connections:
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "retail-robot-agents-demo",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "websocket_clients": len(active_connections),
        "demo_running": demo_running,
    }


@app.get("/api/inventory")
async def get_inventory():
    """Pull real luxury products from MongoDB."""
    try:
        products = fetch_luxury_inventory(limit=50)
        return {
            "status": "ok",
            "count": len(products),
            "products": products,
        }
    except Exception as exc:
        logger.error("Inventory fetch failed: %s", exc)
        return {
            "status": "error",
            "message": str(exc),
            "products": [],
        }


class CustomerProfileRequest(BaseModel):
    customer_id: str = "demo_customer_001"
    name: str = "Alexandra Chen"
    sizes: dict = {"tops": "S", "bottoms": "26"}
    style_tags: list[str] = ["minimalist", "luxury", "business"]
    budget_max: float = 2500
    preferred_brands: list[str] = ["Saint Laurent", "Prada", "Bottega Veneta"]
    occasion: str = "business dinner"


@app.post("/api/demo/run")
async def run_demo_endpoint(profile: CustomerProfileRequest | None = None):
    """
    Trigger a demo run. Broadcasts events over WebSocket /ws/demo.
    """
    global demo_running
    if demo_running:
        return {"status": "already_running", "message": "Demo is already in progress"}

    profile_data = profile.model_dump() if profile else DEMO_CUSTOMER

    demo_running = True

    async def _run():
        global demo_running
        try:
            await run_demo(broadcast_to_all, profile_data)
        except Exception as exc:
            logger.error("Demo runner error: %s", exc)
            await broadcast_to_all({
                "type": "error",
                "message": f"Demo error: {exc}",
                "data": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        finally:
            demo_running = False

    asyncio.create_task(_run())

    return {
        "status": "started",
        "message": "Demo started — connect to /ws/demo for live events",
        "customer": profile_data.get("name"),
    }


@app.websocket("/ws/demo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("WebSocket client connected (total: %d)", len(active_connections))

    # Send welcome event
    await websocket.send_text(json.dumps({
        "type": "agent",
        "message": "🔌 Connected to Retail Robot Agents demo stream",
        "data": {"connected": True, "demo_running": demo_running},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }))

    try:
        while True:
            # Keep connection alive — client messages are ignored (just heartbeats)
            data = await websocket.receive_text()
            logger.debug("WS message from client: %s", data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected (total: %d)", len(active_connections))
    except Exception as exc:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.error("WebSocket error: %s", exc)
