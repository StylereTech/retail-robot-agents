"""
Inventory API — mock store database.
In production, connects to MongoDB dirty_apple_prod or retailer POS system.
"""
from __future__ import annotations
import asyncio

MOCK_INVENTORY = [
    {"sku": "SL-BLZ-M-BLK", "brand": "Saint Laurent", "name": "Classic Blazer",
     "size": "M", "color": "black", "category": "blazer", "ourPrice": 890.00,
     "inStock": True, "location": {"aisle": "W4", "rack": 3, "position": 7}},
    {"sku": "GUC-HOOD-M-BLK", "brand": "Gucci", "name": "GG Embroidered Hoodie",
     "size": "M", "color": "black", "category": "hoodie", "ourPrice": 680.00,
     "inStock": True, "location": {"aisle": "M2", "rack": 1, "position": 3}},
    {"sku": "PRA-DRESS-L-BLU", "brand": "Prada", "name": "Re-Nylon Shirt Dress",
     "size": "L", "color": "blue", "category": "dress", "ourPrice": 1100.00,
     "inStock": True, "location": {"aisle": "W2", "rack": 5, "position": 1}},
    {"sku": "BUR-HOOD-M-BEI", "brand": "Burberry", "name": "Vintage Check Hoodie",
     "size": "M", "color": "beige", "category": "hoodie", "ourPrice": 490.00,
     "inStock": True, "location": {"aisle": "M3", "rack": 2, "position": 5}},
    {"sku": "AMR-HOOD-M-BLK", "brand": "Amiri", "name": "Paint Drip Hoodie",
     "size": "M", "color": "black", "category": "hoodie", "ourPrice": 580.00,
     "inStock": True, "location": {"aisle": "M4", "rack": 1, "position": 2}},
    {"sku": "VAL-BAG-MED-BLK", "brand": "Valentino", "name": "VLogo Chain Shoulder Bag",
     "size": "Medium", "color": "black", "category": "bag", "ourPrice": 1350.00,
     "inStock": True, "location": {"aisle": "A1", "rack": 4, "position": 6}},
]


class InventoryAPI:
    """Mock inventory interface. Swap for real MongoDB/POS in production."""

    async def search(self, size: str = None, color: str = None,
                     category: str = None, max_price: float = None) -> list[dict]:
        await asyncio.sleep(0.1)  # simulate DB query
        results = []
        for item in MOCK_INVENTORY:
            if not item["inStock"]:
                continue
            if size and item["size"].upper() != size.upper():
                continue
            if color and item["color"].lower() != color.lower():
                continue
            if category and category.lower() not in item["category"].lower():
                continue
            if max_price and item["ourPrice"] > max_price:
                continue
            results.append(item)
        return results

    async def get_by_sku(self, sku: str) -> dict | None:
        await asyncio.sleep(0.05)
        return next((i for i in MOCK_INVENTORY if i["sku"] == sku), None)

    async def mark_picked(self, sku: str) -> bool:
        for item in MOCK_INVENTORY:
            if item["sku"] == sku:
                item["inStock"] = False
                return True
        return False
