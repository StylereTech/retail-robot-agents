"""
Return Handler — processes customer returns and restocks inventory.
"""
from __future__ import annotations
import asyncio
from retail_utils.inventory_api import InventoryAPI, MOCK_INVENTORY


class ReturnHandler:
    def __init__(self):
        self.inventory = InventoryAPI()
        self.pending_returns: list[dict] = []

    async def schedule_pickup(self, order_id: str, skus: list[str],
                               address: str) -> dict:
        entry = {"order_id": order_id, "skus": skus,
                 "address": address, "status": "scheduled"}
        self.pending_returns.append(entry)
        print(f"  📦 Return scheduled: {len(skus)} items from {address}")
        return entry

    async def process_return(self, order_id: str) -> dict:
        entry = next((r for r in self.pending_returns
                      if r["order_id"] == order_id), None)
        if not entry:
            return {"error": "Return not found"}
        for sku in entry["skus"]:
            for item in MOCK_INVENTORY:
                if item["sku"] == sku:
                    item["inStock"] = True
                    print(f"  🔄 Restocked: {sku}")
        entry["status"] = "restocked"
        return entry
