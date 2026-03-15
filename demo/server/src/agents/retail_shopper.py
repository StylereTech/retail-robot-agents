"""
Retail Shopper Agent — OpenClaw skill-driven
Browses store inventory, understands customer intent, generates pick list.
Skills: search_inventory, rank_by_preference, generate_pick_list
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Optional
from retail_utils.inventory_api import InventoryAPI
from protocols.arp import PickList, PickItem, ItemLocation, DeliveryDetails
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class RetailShopperAgent:
    """
    OpenClaw agent that handles the full shopping flow:
    1. Parses customer request (natural language)
    2. Searches live inventory
    3. Ranks results by customer profile
    4. Returns curated pick list for the robot
    """

    def __init__(self):
        self.inventory = InventoryAPI()

    async def shop(self, customer_id: str, request: str, profile: dict = None) -> PickList:
        """Main entry point — takes natural language request, returns robot pick list."""
        print(f"\n🧠 Agent processing: '{request}'")

        # Step 1: Parse intent
        intent = self._parse_intent(request)
        print(f"   Intent: {intent}")

        # Step 2: Search inventory
        results = await self.inventory.search(**intent)
        print(f"   Found {len(results)} matching items")

        if not results:
            raise ValueError(f"No items found matching: {request}")

        # Step 3: Rank by customer profile
        ranked = self._rank(results, profile or {})

        # Step 4: Build pick list (top 3)
        items = []
        for i, item in enumerate(ranked[:3]):
            items.append(PickItem(
                sku=item["sku"],
                brand=item["brand"],
                item=item["name"],
                size=item["size"],
                color=item["color"],
                location=ItemLocation(**item["location"]),
                priority=i + 1
            ))

        return PickList(
            session_id=f"shop-{customer_id}-{abs(hash(request)) % 10000:04d}",
            customer_id=customer_id,
            store_id="store_001",
            items=items,
            delivery=DeliveryDetails(type="home_delivery", window="2h")
        )

    def _parse_intent(self, text: str) -> dict:
        """Simple keyword parser — replace with LLM in production."""
        text_lower = text.lower()
        intent = {}

        # Size detection
        for size in ["xs", "s", "m", "l", "xl", "xxl"]:
            if f" {size} " in f" {text_lower} " or f"size {size}" in text_lower:
                intent["size"] = size.upper()
                break

        # Color detection
        for color in ["black", "white", "blue", "red", "green", "grey", "gray", "beige", "tan", "brown"]:
            if color in text_lower:
                intent["color"] = color
                break

        # Category detection
        for cat in ["hoodie", "dress", "blazer", "bag", "sneaker", "jacket", "shirt", "pants", "skirt"]:
            if cat in text_lower:
                intent["category"] = cat
                break

        # Budget detection
        import re
        budget = re.search(r'\$?(\d+)', text)
        if budget:
            intent["max_price"] = float(budget.group(1))

        return intent

    def _rank(self, items: list, profile: dict) -> list:
        """Rank items by profile match."""
        preferred_brands = profile.get("preferred_brands", [])
        scored = []
        for item in items:
            score = 0
            if item.get("brand") in preferred_brands:
                score += 5
            if item.get("ourPrice", 999) <= profile.get("budget_max", 9999):
                score += 3
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored]
