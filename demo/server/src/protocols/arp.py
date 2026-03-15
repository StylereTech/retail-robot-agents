"""
Agent-Robot Protocol (ARP)
Defines the message schema between OpenClaw agents and in-store robots.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ItemLocation:
    aisle: str
    rack: int
    position: int


@dataclass
class PickItem:
    sku: str
    brand: str
    item: str
    size: str
    color: str
    location: ItemLocation
    priority: int = 1
    picked: bool = False


@dataclass
class DeliveryDetails:
    type: str  # "home_delivery", "curbside", "in_store_pickup"
    address: Optional[str] = None
    window: str = "2h"


@dataclass
class PickList:
    session_id: str
    customer_id: str
    store_id: str
    items: list
    delivery: DeliveryDetails
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"

    def pending_items(self):
        return [i for i in self.items if not i.picked]

    def is_complete(self):
        return all(i.picked for i in self.items)


@dataclass
class ReturnRequest:
    order_id: str
    customer_id: str
    items: list
    pickup_address: str
    reason: Optional[str] = None
    status: str = "scheduled"
