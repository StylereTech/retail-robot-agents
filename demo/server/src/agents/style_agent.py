"""
StyleAgent — AI Personal Stylist
Learns customer preferences and curates a try-on box.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CustomerProfile:
    customer_id: str
    sizes: dict = field(default_factory=dict)       # {"tops": "M", "pants": "32x30", "shoes": "10"}
    style_tags: list[str] = field(default_factory=list)  # ["minimalist", "streetwear", "business"]
    budget_max: float = 500.0
    preferred_brands: list[str] = field(default_factory=list)
    occasion: Optional[str] = None                  # "work", "casual", "date night", "event"


class StyleAgent:
    """
    Learns a customer's style and curates a personalized try-on selection.
    Works with ShopperAgent to find items matching the curation.
    """

    def __init__(self):
        self.profiles: dict[str, CustomerProfile] = {}
        logger.info("StyleAgent initialized")

    def update_profile(self, customer_id: str, **kwargs) -> CustomerProfile:
        profile = self.profiles.get(customer_id, CustomerProfile(customer_id=customer_id))
        for k, v in kwargs.items():
            if hasattr(profile, k):
                setattr(profile, k, v)
        self.profiles[customer_id] = profile
        logger.info("Profile updated for %s: %s", customer_id, kwargs)
        return profile

    def curate(self, customer_id: str, catalog: list[dict], max_items: int = 5) -> list[dict]:
        """
        Select items from catalog that best match the customer's profile.
        Returns a curated list for the pick list agent.
        """
        profile = self.profiles.get(customer_id)
        if not profile:
            logger.warning("No profile for %s — returning top %d items", customer_id, max_items)
            return catalog[:max_items]

        scored = []
        for item in catalog:
            score = 0
            # Brand match
            if item.get("brand") in profile.preferred_brands:
                score += 3
            # Budget fit
            price = item.get("ourPrice", 9999)
            if price <= profile.budget_max:
                score += 2
            # Style tag overlap
            item_tags = item.get("tags", [])
            overlap = set(item_tags) & set(profile.style_tags)
            score += len(overlap)
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        curated = [item for _, item in scored[:max_items]]
        logger.info("Curated %d items for customer %s", len(curated), customer_id)
        return curated
