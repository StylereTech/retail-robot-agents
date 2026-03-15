"""
Demo Runner — orchestrates the full retail robot demo flow.
Pulls real products from MongoDB, runs StyleAgent + RobotControllerAgent,
broadcasts events over WebSocket.
"""
from __future__ import annotations
import sys
import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

sys.path.insert(0, '/tmp/retail-robot-agents/src')

from pymongo import MongoClient
from agents.style_agent import StyleAgent, CustomerProfile
from agents.robot_controller import RobotControllerAgent

MONGODB_URI = (
    "mongodb+srv://styleredev:Style2026@cluster0.tog9ftx.mongodb.net/"
    "dirty_apple_prod?retryWrites=true&w=majority"
)

LUXURY_BRANDS = ["Saint Laurent", "Gucci", "Prada", "Burberry", "Versace", "Bottega Veneta"]

DEMO_CUSTOMER = {
    "customer_id": "demo_customer_001",
    "name": "Alexandra Chen",
    "sizes": {"tops": "S", "bottoms": "26"},
    "style_tags": ["minimalist", "luxury", "business"],
    "budget_max": 2500,
    "preferred_brands": ["Saint Laurent", "Prada", "Bottega Veneta"],
    "occasion": "business dinner",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(type_: str, message: str, data: Any = None) -> dict:
    return {
        "type": type_,
        "message": message,
        "data": data or {},
        "timestamp": _now(),
    }


def fetch_luxury_inventory(limit: int = 30) -> list[dict]:
    """Pull luxury products from MongoDB."""
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=8000)
    db = client["dirty_apple_prod"]
    collection = db["products"]

    query = {"brand": {"$in": LUXURY_BRANDS}}
    projection = {
        "_id": 0,
        "brand": 1,
        "productName": 1,
        "ourPrice": 1,
        "imageUrl": 1,
        "tags": 1,
        "sku": 1,
        "category": 1,
    }

    cursor = collection.find(query, projection).limit(limit)
    products = list(cursor)
    client.close()
    return products


async def run_demo(
    broadcast: Callable[[dict], Awaitable[None]],
    customer_profile: dict | None = None,
) -> None:
    """
    Full demo orchestration. Broadcasts WebSocket events at each step.
    """
    profile_data = customer_profile or DEMO_CUSTOMER

    # ── Step 1: Init ────────────────────────────────────────────────────────
    await broadcast(_event("agent", "🤖 StyleAgent initializing…", {"customer": profile_data.get("name")}))
    await asyncio.sleep(1)

    # ── Step 2: Fetch inventory ──────────────────────────────────────────────
    await broadcast(_event("agent", "📦 Pulling luxury inventory from MongoDB…"))
    await asyncio.sleep(1)

    try:
        catalog = fetch_luxury_inventory()
    except Exception as exc:
        # Fall back to mock data if DB unreachable
        catalog = _mock_catalog()
        await broadcast(_event("agent", f"⚠️ DB fallback (sim mode): {exc}", {"sim": True}))

    await broadcast(_event(
        "agent",
        f"✅ Found {len(catalog)} luxury items across {len(LUXURY_BRANDS)} brands",
        {"brands": list({p.get('brand') for p in catalog}), "count": len(catalog)},
    ))
    await asyncio.sleep(1.5)

    # ── Step 3: StyleAgent curates ───────────────────────────────────────────
    await broadcast(_event("agent", "🎨 StyleAgent analyzing customer profile…", {
        "tags": profile_data.get("style_tags"),
        "occasion": profile_data.get("occasion"),
        "budget": profile_data.get("budget_max"),
    }))
    await asyncio.sleep(1.5)

    style_agent = StyleAgent()
    cid = profile_data["customer_id"]
    style_agent.update_profile(
        cid,
        sizes=profile_data.get("sizes", {}),
        style_tags=profile_data.get("style_tags", []),
        budget_max=profile_data.get("budget_max", 2500),
        preferred_brands=profile_data.get("preferred_brands", []),
        occasion=profile_data.get("occasion"),
    )

    curated = style_agent.curate(cid, catalog, max_items=3)

    # Ensure we always have 3 items (fill from mock if needed)
    if len(curated) < 3:
        curated += _mock_catalog()[: 3 - len(curated)]

    await broadcast(_event("agent", f"✨ Curated {len(curated)} perfect items for {profile_data.get('name')}", {
        "items": [{"brand": i.get("brand"), "name": i.get("productName"), "price": i.get("ourPrice")} for i in curated],
    }))
    await asyncio.sleep(1.5)

    # ── Step 4: Robot picks items ────────────────────────────────────────────
    robot = RobotControllerAgent(sim=True)
    await broadcast(_event("robot", "🦾 RobotControllerAgent online — beginning pick sequence"))
    await asyncio.sleep(1)

    picked_items = []
    for idx, item in enumerate(curated):
        await broadcast(_event("robot", f"🏃 Navigating to shelf — {item.get('brand', 'Brand')} section", {
            "step": "navigate",
            "item_index": idx,
        }))
        await asyncio.sleep(1.5)

        coords = [idx * 2.5, 1.0, 0.8]
        task = {
            "task_id": f"pick-{idx + 1}",
            "type": "pick",
            "target": {"coordinates": coords, "item": item.get("productName", "Item")},
            "priority": 3 - idx,
            "status": "pending",
        }
        await robot.receive_task(task)
        result = await robot.execute_next()

        picked_items.append(item)
        await broadcast(_event("robot", f"✅ Picked: {item.get('brand')} — {item.get('productName', 'Item')}", {
            "step": "pick",
            "item": {
                "brand": item.get("brand"),
                "name": item.get("productName"),
                "price": item.get("ourPrice"),
                "imageUrl": item.get("imageUrl"),
                "sku": item.get("sku"),
            },
            "robot_result": result,
        }))
        await asyncio.sleep(2)

    # ── Step 5: Return to base ───────────────────────────────────────────────
    await broadcast(_event("robot", "🏠 Returning to dispatch station…", {"step": "return"}))
    await asyncio.sleep(1.5)

    # ── Step 6: Dispatch ─────────────────────────────────────────────────────
    total = sum(i.get("ourPrice", 0) for i in picked_items if isinstance(i.get("ourPrice"), (int, float)))
    await broadcast(_event("dispatch", "📬 Preparing Style.re dispatch package…", {
        "items_count": len(picked_items),
        "total": round(total, 2),
        "customer": profile_data.get("name"),
    }))
    await asyncio.sleep(1.5)

    await broadcast(_event("dispatch", "🚗 DoorDash driver assigned — en route to customer", {
        "driver": "Michael R.",
        "eta_minutes": 42,
        "status": "picked_up",
    }))
    await asyncio.sleep(1.5)

    await broadcast(_event("dispatch", "📍 Package out for delivery", {
        "tracking_steps": [
            {"label": "Order Placed", "done": True},
            {"label": "Items Picked", "done": True},
            {"label": "Driver Assigned", "done": True},
            {"label": "Out for Delivery", "done": True},
            {"label": "Delivered", "done": False},
        ],
    }))
    await asyncio.sleep(1)

    # ── Step 7: Complete ─────────────────────────────────────────────────────
    await broadcast(_event("complete", "🎉 Demo complete! Style.re delivery on the way.", {
        "customer": profile_data.get("name"),
        "items": [
            {
                "brand": i.get("brand"),
                "name": i.get("productName"),
                "price": i.get("ourPrice"),
                "imageUrl": i.get("imageUrl"),
            }
            for i in picked_items
        ],
        "total": round(total, 2),
        "robot_status": robot.status(),
    }))


def _mock_catalog() -> list[dict]:
    """Fallback mock catalog when DB is unreachable."""
    return [
        {
            "brand": "Saint Laurent",
            "productName": "Classic Blazer",
            "ourPrice": 1890.0,
            "imageUrl": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400",
            "tags": ["minimalist", "luxury", "business"],
            "sku": "SL-BLZ-001",
            "category": "Tops",
        },
        {
            "brand": "Prada",
            "productName": "Nylon Shoulder Bag",
            "ourPrice": 1250.0,
            "imageUrl": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400",
            "tags": ["luxury", "minimalist"],
            "sku": "PR-BAG-002",
            "category": "Accessories",
        },
        {
            "brand": "Bottega Veneta",
            "productName": "Intrecciato Loafers",
            "ourPrice": 850.0,
            "imageUrl": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400",
            "tags": ["luxury", "business"],
            "sku": "BV-SHO-003",
            "category": "Shoes",
        },
        {
            "brand": "Gucci",
            "productName": "GG Marmont Belt",
            "ourPrice": 490.0,
            "imageUrl": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
            "tags": ["luxury"],
            "sku": "GC-BLT-004",
            "category": "Accessories",
        },
        {
            "brand": "Burberry",
            "productName": "Heritage Check Scarf",
            "ourPrice": 420.0,
            "imageUrl": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=400",
            "tags": ["luxury", "business"],
            "sku": "BB-SCF-005",
            "category": "Accessories",
        },
    ]
