"""
Curbside Pickup Demo — Full End-to-End
Customer sends natural language request → Agent shops → Robot picks → Curbside handoff

Run: python examples/curbside_pickup_demo.py
"""
import asyncio
import sys
sys.path.insert(0, "src")

from agents.retail_shopper import RetailShopperAgent
from agents.delivery_coordinator import DeliveryCoordinatorAgent
from agents.robot_controller import RobotControllerAgent
from retail_utils.return_handler import ReturnHandler


async def main():
    print("\n" + "="*62)
    print("  🦞 Retail Robot Agents — Curbside Pickup Demo")
    print("  Agent shops. Robot picks. We deliver. No humans needed.")
    print("="*62)

    # --- Agents ---
    shopper    = RetailShopperAgent()
    robot      = RobotControllerAgent(sim=True)
    coordinator = DeliveryCoordinatorAgent()
    returns    = ReturnHandler()

    customer_id = "cust_ry_001"
    customer_profile = {
        "preferred_brands": ["Gucci", "Amiri", "Burberry"],
        "budget_max": 800.0,
    }

    # ── STEP 1: Customer talks to agent ───────────────────────────
    print(f"\n📱 Customer: 'Find me a size M black hoodie under $700'")
    pick_list = await shopper.shop(
        customer_id=customer_id,
        request="Find me a size M black hoodie under $700",
        profile=customer_profile
    )
    print(f"\n   Agent curated {len(pick_list.items)} item(s):")
    for item in pick_list.items:
        print(f"   • {item.brand} — {item.item} ({item.size}, {item.color})")
        print(f"     📍 Aisle {item.location.aisle}, Rack {item.location.rack}, Pos {item.location.position}")

    # ── STEP 2: Robot picks from shelves ──────────────────────────
    print(f"\n🤖 Dispatching in-store robot...")
    for pick_item in pick_list.items:
        await robot.receive_task({
            "task_id": f"pick-{pick_item.sku}",
            "type": "pick",
            "target": {
                "coordinates": [pick_item.location.rack * 2.5, pick_item.location.position * 1.2, 1.1],
                "item": f"{pick_item.brand} {pick_item.item}",
                "sku": pick_item.sku,
            },
            "priority": pick_item.priority
        })
    while True:
        result = await robot.execute_next()
        if result["status"] == "completed":
            print(f"   ✅ Picked: {result['task_id'].replace('pick-', '')}")
        elif result["status"] == "idle":
            break

    # ── STEP 3: Dispatch for delivery ─────────────────────────────
    pick_list.delivery.type = "curbside"
    pick_list.delivery.address = "1234 Oak Cliff Blvd, Dallas TX 75203"
    delivery = await coordinator.dispatch(pick_list)
    print(f"   🚗 Driver en route — ETA {delivery.eta_minutes} min")

    # ── STEP 4: Customer tries on, keeps 1, returns 1 ─────────────
    print(f"\n👕 Customer tries on at home...")
    kept = [pick_list.items[0].sku]
    returned = [item.sku for item in pick_list.items[1:]]

    if kept:
        result = await coordinator.confirm_kept(pick_list.session_id, kept)
        print(f"   💳 Kept & charged: {kept}")

    if returned:
        ret = await coordinator.handle_return(
            pick_list.session_id, returned,
            pick_list.delivery.address
        )
        restock = await returns.schedule_pickup(
            pick_list.session_id, returned, pick_list.delivery.address
        )

    # ── SUMMARY ───────────────────────────────────────────────────
    print(f"\n{'='*62}")
    print(f"  ✅ Order complete")
    print(f"  Kept: {len(kept)} item(s) | Returned: {len(returned)} item(s)")
    print(f"  No humans involved at any step.")
    print(f"{'='*62}\n")


if __name__ == "__main__":
    asyncio.run(main())
