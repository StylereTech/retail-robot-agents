"""
FastAPI Backend — Retail Robot Agents Demo
Self-contained: no external src/ dependencies.
"""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from demo_runner import run_demo, fetch_luxury_inventory, DEMO_CUSTOMER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Retail Robot Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active = [w for w in self.active if w != ws]

    async def send(self, ws: WebSocket, data: dict):
        try:
            await ws.send_text(json.dumps(data))
        except Exception:
            self.disconnect(ws)


manager = ConnectionManager()


class DemoRequest(BaseModel):
    customer: dict | None = None


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/inventory")
async def get_inventory():
    items = fetch_luxury_inventory(48)
    return {"items": items, "count": len(items)}


@app.post("/api/demo/run")
async def trigger_demo(req: DemoRequest):
    """Trigger demo — events delivered via WebSocket /ws/demo."""
    return {"status": "started", "message": "Connect to /ws/demo for live events"}


@app.websocket("/ws/demo")
async def demo_websocket(ws: WebSocket):
    await manager.connect(ws)
    logger.info("WebSocket client connected")

    try:
        # Wait for start signal from client
        data = await ws.receive_text()
        payload = json.loads(data) if data else {}
        customer = payload.get("customer", DEMO_CUSTOMER)

        async def emit(event: dict):
            await manager.send(ws, event)

        await run_demo(customer, emit)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error("Demo error: %s", e)
        try:
            await ws.send_text(json.dumps({
                "type": "error",
                "message": f"Demo error: {str(e)}",
                "data": {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
        except Exception:
            pass
    finally:
        manager.disconnect(ws)
