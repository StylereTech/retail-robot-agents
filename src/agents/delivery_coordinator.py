"""
Delivery Coordinator Agent
Orchestrates the full delivery lifecycle: dispatch → handoff → return.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from protocols.arp import PickList, ReturnRequest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@dataclass
class DeliveryStatus:
    order_id: str
    status: str  # packed, dispatched, delivered, return_scheduled, returned
    eta_minutes: int = 0
    driver_id: str = ""


class DeliveryCoordinatorAgent:
    """
    Manages the full order lifecycle after robot picks:
    1. Confirms pack complete
    2. Dispatches driver via Style.re / DoorDash Drive
    3. Tracks delivery
    4. Handles keep/return decision
    5. Dispatches return pickup if needed
    """

    def __init__(self):
        self.orders: dict[str, DeliveryStatus] = {}

    async def dispatch(self, pick_list: PickList) -> DeliveryStatus:
        print(f"\n🚚 Dispatching order {pick_list.session_id}...")
        # In production: call DoorDash Drive API or Style.re dispatch
        await asyncio.sleep(0.5)  # simulate API call
        status = DeliveryStatus(
            order_id=pick_list.session_id,
            status="dispatched",
            eta_minutes=35,
            driver_id="driver_001"
        )
        self.orders[pick_list.session_id] = status
        print(f"   ✅ Driver assigned. ETA: {status.eta_minutes} min")
        return status

    async def handle_return(self, order_id: str, rejected_skus: list[str],
                             pickup_address: str) -> ReturnRequest:
        print(f"\n🔄 Processing return for order {order_id}...")
        print(f"   Items rejected: {rejected_skus}")
        ret = ReturnRequest(
            order_id=order_id,
            customer_id=f"cust_{order_id[:8]}",
            items=rejected_skus,
            pickup_address=pickup_address,
            reason="customer_return"
        )
        await asyncio.sleep(0.3)
        ret.status = "scheduled"
        print(f"   ✅ Return pickup scheduled for: {pickup_address}")
        return ret

    async def confirm_kept(self, order_id: str, kept_skus: list[str]) -> dict:
        print(f"\n💳 Customer kept {len(kept_skus)} items from order {order_id}")
        # In production: trigger Stripe charge for kept items
        return {"order_id": order_id, "kept": kept_skus, "charged": True}
