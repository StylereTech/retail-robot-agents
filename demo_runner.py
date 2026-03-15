"""
Demo Runner — self-contained, no src/ dependencies.
Iterations 8, 12: accepts preloaded catalog, DEMO_DATA_MODE support.
"""
from __future__ import annotations
import asyncio
import os
import random
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

MONGODB_URI = os.environ.get(
    "MONGODB_URI",
    "mongodb+srv://styleredev:Style2026@cluster0.tog9ftx.mongodb.net/dirty_apple_prod?retryWrites=true&w=majority"
)

DEMO_CUSTOMER = {
    "customer_id": "demo_customer_001",
    "name": "Alexandra Chen",
    "sizes": {"tops": "S", "bottoms": "26"},
    "style_tags": ["minimalist", "luxury", "business"],
    "budget_max": 2500,
    "preferred_brands": ["Saint Laurent", "Prada", "Bottega Veneta", "Gucci", "Burberry"],
    "occasion": "business dinner"
}

LUXURY_BRANDS = [
    "Saint Laurent", "Prada", "Bottega Veneta", "Gucci", "Burberry",
    "Versace", "Tom Ford", "Balmain"
]

CURATED_CATALOG = [
    {"brand": "Saint Laurent", "name": "Classic Tuxedo Blazer", "ourPrice": 2890.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/yslms/yslms3041702/yslms3041702_1-0_g._SL3000_.jpg",
     "category": "clothing"},
    {"brand": "Prada", "name": "Re-Nylon Tote Bag", "ourPrice": 1250.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/prd/prd3027040/prd3027040_1-0_g._SL3000_.jpg",
     "category": "bags"},
    {"brand": "Bottega Veneta", "name": "The Pouch Clutch", "ourPrice": 2200.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/bttgvnt/bttgvnt30087765/bttgvnt30087765_1-0_g._SL3000_.jpg",
     "category": "bags"},
    {"brand": "Gucci", "name": "Horsebit 1955 Loafers", "ourPrice": 890.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/guc/guc60272344/guc60272344_1-0_g._SL3000_.jpg",
     "category": "shoes"},
    {"brand": "Burberry", "name": "Classic Westminster Trench", "ourPrice": 1990.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/brbry/brbry30074538/brbry30074538_1-0_g._SL3000_.jpg",
     "category": "clothing"},
    {"brand": "Tom Ford", "name": "Silk Charmeuse Blouse", "ourPrice": 650.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/tomfrd/tomfrd3015698/tomfrd3015698_1-0_g._SL3000_.jpg",
     "category": "clothing"},
    {"brand": "Versace", "name": "Medusa Chain Heels", "ourPrice": 995.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/vrsace/vrsace3030452/vrsace3030452_1-0_g._SL3000_.jpg",
     "category": "shoes"},
    {"brand": "Balmain", "name": "Structured Tweed Blazer", "ourPrice": 3200.00,
     "imageUrl": "https://m.media-amazon.com/images/G/01/Shopbop/p/prod/products/blmain/blmain3022190/blmain3022190_1-0_g._SL3000_.jpg",
     "category": "clothing"},
]


def fetch_luxury_inventory(limit: int = 50, mode: str = "live") -> list[dict]:
    if mode == "mock" or mode == "curated":
        return CURATED_CATALOG
    if not MONGO_AVAILABLE:
        return CURATED_CATALOG
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client["dirty_apple_prod"]
        products = list(db.products.find(
            {"brand": {"$in": LUXURY_BRANDS}, "imageUrl": {"$exists": True, "$ne": ""}},
            {"brand": 1, "name": 1, "ourPrice": 1, "imageUrl": 1, "category": 1, "_id": 0}
        ).limit(limit))
        client.close()
        return products if len(products) >= 6 else CURATED_CATALOG
    except Exception:
        return CURATED_CATALOG


def curate_items(customer: dict, catalog: list[dict], n: int = 3) -> list[dict]:
    preferred = set(b.lower() for b in customer.get("preferred_brands", []))
    budget = customer.get("budget_max", 9999)
    scored = []
    for item in catalog:
        score = (2 if item.get("brand", "").lower() in preferred else 0) + \
                (1 if float(item.get("ourPrice", 0)) <= budget else 0)
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [item for _, item in scored[:n]]
    return selected if selected else catalog[:n]


async def run_demo(
    customer: dict,
    emit: Callable[[dict], Awaitable[None]],
    catalog: list[dict] | None = None
) -> None:
    def event(type_: str, message: str, data: Any = None) -> dict:
        return {"type": type_, "message": message, "data": data or {},
                "timestamp": datetime.now(timezone.utc).isoformat()}

    # Step 1: Profile
    await emit(event("agent", f"🧠 StyleAgent initializing for {customer.get('name', 'Guest')}..."))
    await asyncio.sleep(1.2)
    await emit(event("agent",
        f"📋 Profile: {', '.join(customer.get('style_tags', []))} | Budget: ${customer.get('budget_max', 0):,.0f}",
        {"profile": customer}))
    await asyncio.sleep(1.0)
    await emit(event("agent",
        f"🎯 Occasion: {customer.get('occasion','event')} | Brands: {', '.join(customer.get('preferred_brands', [])[:3])}"))
    await asyncio.sleep(0.8)

    # Step 2: Inventory
    await emit(event("agent", "🔍 Scanning live luxury inventory from database..."))
    await asyncio.sleep(1.0)
    if catalog is None:
        mode = os.environ.get("DEMO_DATA_MODE", "live")
        catalog = fetch_luxury_inventory(50, mode=mode)
    await emit(event("agent", f"✅ {len(catalog)} luxury items loaded from catalog", {"catalog_size": len(catalog)}))
    await asyncio.sleep(0.8)

    # Step 3: Curation
    await emit(event("agent", "🤖 StyleAgent curating personalized try-on box..."))
    await asyncio.sleep(1.5)
    selected = curate_items(customer, catalog, n=3)
    for i, item in enumerate(selected):
        await emit(event("agent",
            f"✓ Selected: {item.get('brand')} — {item.get('name')} (${float(item.get('ourPrice', 0)):,.2f})",
            {"item": item, "index": i}))
        await asyncio.sleep(0.6)
    total = sum(float(item.get("ourPrice", 0)) for item in selected)
    await emit(event("agent", f"📦 Try-on box curated: {len(selected)} items | Est. value: ${total:,.2f}",
        {"items": selected, "total": total}))
    await asyncio.sleep(1.0)

    # Step 4: ARP
    await emit(event("robot", "📋 Generating ARP pick list...", {"step": "navigate"}))
    await asyncio.sleep(1.0)
    pick_list = []
    for item in selected:
        sku = f"{item.get('brand','XX')[:3].upper()}-{item.get('category','ITEM')[:3].upper()}-{random.randint(100,999)}"
        pick_list.append({
            "sku": sku, "name": item.get("name"), "brand": item.get("brand"),
            "ourPrice": float(item.get("ourPrice", 0)), "imageUrl": item.get("imageUrl", ""),
            "category": item.get("category", ""), "aisle": f"A{random.randint(1,5)}", "shelf": random.randint(1,8)
        })
    await emit(event("robot", f"✅ ARP ready: {len(pick_list)} picks | Route optimized", {"pick_list": pick_list}))
    await asyncio.sleep(0.8)

    # Step 5: Robot picks
    await emit(event("robot", "🤖 LobsterBox™ arm activating...", {"step": "navigate"}))
    await asyncio.sleep(1.5)
    for i, pick in enumerate(pick_list):
        await emit(event("robot", f"🦾 → Aisle {pick['aisle']}, Shelf {pick['shelf']}", {"step": "navigate"}))
        await asyncio.sleep(1.2)
        await emit(event("robot", f"🔍 Scanning: {pick['sku']}", {"step": "pick"}))
        await asyncio.sleep(0.8)
        await emit(event("robot", f"✅ PICKED: {pick['brand']} — {pick['name']}",
            {"step": "pick", "picked": pick, "index": i, "progress": (i+1)/len(pick_list)}))
        await asyncio.sleep(1.0)
    await emit(event("robot", "📦 Returning to base...", {"step": "return"}))
    await asyncio.sleep(1.5)
    await emit(event("robot", f"✅ LobsterBox™ complete — {len(pick_list)}/{len(pick_list)} secured",
        {"step": "done", "all_picked": pick_list}))
    await asyncio.sleep(1.0)

    # Step 6: Dispatch
    tracking_steps = [
        {"label": "AI curation complete", "done": True},
        {"label": "Robot pick complete", "done": True},
        {"label": "Payment pre-authorized", "done": False},
        {"label": "Driver assigned", "done": False},
        {"label": "Out for delivery", "done": False},
    ]
    await emit(event("dispatch", "🚀 Initiating Style.re dispatch...", {"tracking_steps": tracking_steps}))
    await asyncio.sleep(1.0)
    tracking_steps[2]["done"] = True
    await emit(event("dispatch", "💳 Payment pre-authorized | SMS sent",
        {"tracking_steps": tracking_steps, "total": round(total, 2)}))
    await asyncio.sleep(0.8)
    tracking_steps[3]["done"] = True
    await emit(event("dispatch", "🚗 DoorDash driver assigned — ETA 23 min", {"tracking_steps": tracking_steps}))
    await asyncio.sleep(1.0)
    tracking_steps[4]["done"] = True
    await emit(event("dispatch", f"📍 Delivering to {customer.get('name','Customer')} | Dallas, TX",
        {"tracking_steps": tracking_steps, "driver": "Marcus T.", "eta_minutes": 23}))
    await asyncio.sleep(1.0)

    # Complete
    await emit(event("complete", "🎉 Full cycle complete: AI curated → Robot picked → Driver dispatched",
        {"summary": {"customer": customer.get("name","Guest"), "items_picked": len(selected),
                      "total_value": round(total, 2), "eta_minutes": 23},
         "total": round(total, 2)}))
