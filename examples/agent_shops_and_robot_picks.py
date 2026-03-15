"""
Full End-to-End Demo: Agent shops → Robot picks → Ready for delivery

Simulates the complete Style.re AI Robotics flow:
1. StyleAgent curates a try-on box for the customer
2. PickListAgent generates robot instructions
3. RobotControllerAgent executes picks in-store
4. Order is ready for Style.re delivery dispatch

Run: python examples/agent_shops_and_robot_picks.py
"""
import asyncio
import sys
sys.path.insert(0, "src")

from agents.style_agent import StyleAgent, CustomerProfile
from agents.robot_controller import RobotControllerAgent
from protocols.arp import PickList, PickItem, ItemLocation, DeliveryDetails


# --- Sample catalog (in production, this comes from MongoDB / Style.re API) ---
SAMPLE_CATALOG = [
    {"sku": "SL-BLZ-38-BLK", "brand": "Saint Laurent", "name": "Classic Blazer",
     "size": "38", "color": "Black", "ourPrice": 890.00, "tags": ["minimalist", "business"],
     "location": {"aisle": "W4", "rack": 3, "position": 7}},
    {"sku": "GUC-BAG-MED-TAN", "brand": "Gucci", "name": "GG Marmont Shoulder Bag",
     "size": "Medium", "color": "Tan", "ourPrice": 1250.00, "tags": ["luxury", "everyday"],
     "location": {"aisle": "A2", "rack": 1, "position": 2}},
    {"sku": "PRA-DRESS-S-BLK", "brand": "Prada", "name": "Re-Nylon Shirt Dress",
     "size": "S", "color": "Black", "ourPrice": 1100.00, "tags": ["minimalist", "event"],
     "location": {"aisle": "W2", "rack": 5, "position": 1}},
    {"sku": "BUR-SCARF-ONE-BEI", "brand": "Burberry", "name": "Vintage Check Scarf",
     "size": "One Size", "color": "Beige", "ourPrice": 390.00, "tags": ["classic", "everyday"],
     "location": {"aisle": "A5", "rack": 2, "position": 4}},
]


async def main():
    print("\n" + "="*60)
    print("  Style.re AI Robotics OPC — Full Demo")
    print("  Agent shops. Robot picks. We deliver.")
    print("="*60 + "\n")

    # Step 1: Style Agent learns customer preferences
    print("🧠 Step 1: StyleAgent building customer profile...")
    style_agent = StyleAgent()
    profile = style_agent.update_profile(
        customer_id="cust_ry_001",
        sizes={"tops": "M", "pants": "32x30"},
        style_tags=["minimalist", "business", "luxury"],
        budget_max=1500.0,
        preferred_brands=["Saint Laurent", "Prada", "Gucci"],
        occasion="business casual"
    )
    print(f"   Profile: {profile.occasion} | Budget: ${profile.budget_max} | Brands: {profile.preferred_brands[:2]}...\n")

    # Step 2: Agent curates try-on box from catalog
    print("🛍️  Step 2: Agent curating try-on box...")
    curated = style_agent.curate("cust_ry_001", SAMPLE_CATALOG, max_items=3)
    for item in curated:
        print(f"   ✓ {item['brand']} — {item['name']} (${item['ourPrice']:.2f})")
    print()

    # Step 3: Build pick list (Agent-Robot Protocol)
    print("📋 Step 3: Generating robot pick list (ARP)...")
    pick_items = [
        PickItem(
            sku=item["sku"],
            brand=item["brand"],
            item=item["name"],
            size=item["size"],
            color=item["color"],
            location=ItemLocation(**item["location"]),
            priority=i+1
        ) for i, item in enumerate(curated)
    ]
    pick_list = PickList(
        session_id="agent-007-shop-0001",
        customer_id="cust_ry_001",
        store_id="store_dallas_oak_cliff_01",
        items=pick_items,
        delivery=DeliveryDetails(
            type="home_delivery",
            address="1234 Oak Cliff Blvd, Dallas TX 75203",
            window="2h"
        )
    )
    print(f"   Pick list: {len(pick_list.items)} items | Delivery: {pick_list.delivery.window} window\n")

    # Step 4: Robot executes picks
    print("🤖 Step 4: RobotControllerAgent executing picks in-store...")
    robot = RobotControllerAgent(sim=True)

    for pick_item in pick_list.items:
        task_id = await robot.receive_task({
            "task_id": f"pick-{pick_item.sku}",
            "type": "pick",
            "target": {
                "coordinates": [
                    pick_item.location.rack * 3.0,
                    pick_item.location.position * 1.5,
                    1.2
                ],
                "item": f"{pick_item.brand} {pick_item.item}",
                "sku": pick_item.sku,
            },
            "priority": pick_item.priority
        })

    while True:
        result = await robot.execute_next()
        if result["status"] == "completed":
            sku = result["result"].get("coordinates", [])
            print(f"   ✅ Picked: {result['task_id']}")
        elif result["status"] == "idle":
            break

    print()
    print("="*60)
    print("  ✅ All items picked. Order ready for Style.re dispatch.")
    print(f"  📦 {len(pick_list.items)} items → {pick_list.delivery.address}")
    print(f"  ⏱  Delivery window: {pick_list.delivery.window}")
    print("="*60)
    print("\n  Customer receives box. Tries on at home.")
    print("  Keep what you love → pay for those items.")
    print("  Return the rest → one tap, we pick it up.\n")


if __name__ == "__main__":
    asyncio.run(main())
