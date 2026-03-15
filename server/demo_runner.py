"""
Demo Runner — self-contained, no src/ dependencies.
Pulls real products from MongoDB, simulates StyleAgent + RobotAgent,
broadcasts events over WebSocket.
"""
from __future__ import annotations
import asyncio
import random
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

MONGODB_URI = "mongodb+srv://styleredev:Style2026@cluster0.tog9ftx.mongodb.net/dirty_apple_prod?retryWrites=true&w=majority"

DEMO_CUSTOMER = {
    "customer_id": "demo_customer_001",
    "name": "Alexandra Chen",
    "sizes": {"tops": "S", "bottoms": "26"},
    "style_tags": ["minimalist", "luxury", "business"],
    "budget_max": 2500,
    "preferred_brands": ["Saint Laurent", "Prada", "Bottega Veneta", "Gucci", "Burberry"],
    "occasion": "business dinner"
}

LUXURY_BRANDS = ["Saint Laurent", "Prada", "Bottega Veneta", "Gucci", "Burberry", "Versace", "Tom Ford", "Balmain"]

MOCK_CATALOG = [
    {"brand": "Saint Laurent", "name": "Classic Blazer", "ourPrice": 890.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "clothing", "shopstyleId": "mock-1"},
    {"brand": "Prada", "name": "Re-Nylon Tote", "ourPrice": 1250.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "bags", "shopstyleId": "mock-2"},
    {"brand": "Bottega Veneta", "name": "The Pouch Clutch", "ourPrice": 2200.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "bags", "shopstyleId": "mock-3"},
    {"brand": "Gucci", "name": "Horsebit Loafers", "ourPrice": 780.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "shoes", "shopstyleId": "mock-4"},
    {"brand": "Burberry", "name": "Classic Trench Coat", "ourPrice": 1990.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "clothing", "shopstyleId": "mock-5"},
    {"brand": "Tom Ford", "name": "Silk Blouse", "ourPrice": 650.00, "imageUrl": "https://images.shopbop.com/shoot-static-fit/8415252/2060_main.jpg", "category": "clothing", "shopstyleId": "mock-6"},
]


def fetch_luxury_inventory(limit: int = 50) -> list[dict]:
    """Pull real luxury products from MongoDB. Falls back to mock catalog."""
    if not MONGO_AVAILABLE:
        return MOCK_CATALOG

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client["dirty_apple_prod"]
        products = list(db.products.find(
            {"brand": {"$in": LUXURY_BRANDS}, "imageUrl": {"$exists": True}},
            {"brand": 1, "name": 1, "ourPrice": 1, "imageUrl": 1, "category": 1, "_id": 0}
        ).limit(limit))
        client.close()
        return products if products else MOCK_CATALOG
    except Exception:
        return MOCK_CATALOG


def curate_items(customer: dict, catalog: list[dict], n: int = 3) -> list[dict]:
    """StyleAgent logic: filter by preferred brands + budget, return top N."""
    preferred = set(b.lower() for b in customer.get("preferred_brands", []))
    budget = customer.get("budget_max", 9999)

    scored = []
    for item in catalog:
        brand_match = item.get("brand", "").lower() in preferred
        in_budget = float(item.get("ourPrice", 0)) <= budget
        score = (2 if brand_match else 0) + (1 if in_budget else 0)
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [item for _, item in scored[:n]]
    if not selected:
        selected = catalog[:n]
    return selected


async def run_demo(
    customer: dict,
    emit: Callable[[dict], Awaitable[None]]
) -> None:
    """Full demo flow — emits WebSocket events at each step."""

    def event(type_: str, message: str, data: Any = None) -> dict:
        return {
            "type": type_,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Step 1: Profile Analysis
    await emit(event("agent", f"🧠 StyleAgent initializing for {customer['name']}..."))
    await asyncio.sleep(1.2)

    await emit(event("agent", f"📋 Profile loaded: {', '.join(customer['style_tags'])} | Budget: ${customer['budget_max']:,.0f}", {
        "profile": customer
    }))
    await asyncio.sleep(1.0)

    await emit(event("agent", f"🎯 Occasion: {customer['occasion']} | Preferred brands: {', '.join(customer['preferred_brands'][:3])}"))
    await asyncio.sleep(0.8)

    # Step 2: Fetch inventory
    await emit(event("agent", "🔍 Scanning live luxury inventory from database..."))
    await asyncio.sleep(1.5)

    catalog = fetch_luxury_inventory(50)
    await emit(event("agent", f"✅ {len(catalog)} luxury items loaded from catalog", {"catalog_size": len(catalog)}))
    await asyncio.sleep(0.8)

    # Step 3: Curate
    await emit(event("agent", "🤖 StyleAgent curating personalized try-on box..."))
    await asyncio.sleep(1.5)

    selected = curate_items(customer, catalog, n=3)

    for i, item in enumerate(selected):
        await emit(event("agent", f"✓ Selected: {item.get('brand')} — {item.get('name')} (${float(item.get('ourPrice', 0)):,.2f})", {
            "item": item, "index": i
        }))
        await asyncio.sleep(0.6)

    total = sum(float(item.get("ourPrice", 0)) for item in selected)
    await emit(event("agent", f"📦 Try-on box curated: {len(selected)} items | Est. value: ${total:,.2f}", {
        "items": selected,
        "total": total
    }))
    await asyncio.sleep(1.0)

    # Step 4: Generate pick list
    await emit(event("robot", "📋 Generating Autonomous Retail Protocol (ARP) pick list..."))
    await asyncio.sleep(1.0)

    pick_list = []
    for item in selected:
        sku = f"{item.get('brand','XX')[:3].upper()}-{item.get('category','ITEM')[:3].upper()}-{random.randint(100,999)}"
        pick_list.append({"sku": sku, "item": item.get("name"), "brand": item.get("brand"), "aisle": f"A{random.randint(1,5)}", "shelf": random.randint(1, 8)})

    await emit(event("robot", f"✅ ARP generated: {len(pick_list)} picks | Optimized route calculated", {
        "pick_list": pick_list
    }))
    await asyncio.sleep(0.8)

    # Step 5: Robot picks
    await emit(event("robot", "🤖 LobsterBox™ arm activating — moving to home position"))
    await asyncio.sleep(1.5)

    for i, pick in enumerate(pick_list):
        await emit(event("robot", f"🦾 Navigating to Aisle {pick['aisle']}, Shelf {pick['shelf']}..."))
        await asyncio.sleep(1.2)

        await emit(event("robot", f"🔍 Scanning barcode: {pick['sku']}"))
        await asyncio.sleep(0.8)

        await emit(event("robot", f"✅ PICKED: {pick['brand']} — {pick['item']}", {
            "picked": pick,
            "index": i,
            "progress": (i + 1) / len(pick_list)
        }))
        await asyncio.sleep(1.0)

    await emit(event("robot", "📦 All items secured in dispatch box — returning to base"))
    await asyncio.sleep(1.5)

    await emit(event("robot", "✅ LobsterBox™ pick sequence complete — 3/3 items secured", {
        "all_picked": pick_list
    }))
    await asyncio.sleep(1.0)

    # Step 6: Dispatch
    await emit(event("dispatch", "🚀 Initiating Style.re dispatch protocol..."))
    await asyncio.sleep(1.0)

    await emit(event("dispatch", "💳 Payment pre-authorized | Customer notified via SMS"))
    await asyncio.sleep(0.8)

    await emit(event("dispatch", "🚗 DoorDash driver assigned — ETA 23 minutes"))
    await asyncio.sleep(1.0)

    await emit(event("dispatch", f"📍 Delivering to {customer['name']} | 1801 N Pearl St, Dallas TX"))
    await asyncio.sleep(0.8)

    await emit(event("dispatch", "✅ Order dispatched — real-time tracking active", {
        "driver": "Marcus T.",
        "eta_minutes": 23,
        "tracking": "https://stylere.app/track/DEMO-001"
    }))
    await asyncio.sleep(1.0)

    # Complete
    await emit(event("complete", "🎉 Full cycle complete: AI curated → Robot picked → Driver dispatched", {
        "summary": {
            "customer": customer["name"],
            "items_picked": len(selected),
            "total_value": round(total, 2),
            "eta_minutes": 23
        }
    }))
