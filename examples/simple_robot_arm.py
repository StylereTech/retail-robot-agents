"""
Simple Robot Arm Demo — Pick and Place via OpenClaw Agent
Run: python examples/simple_robot_arm.py
"""
import asyncio
import sys
sys.path.insert(0, "src")

from agents.robot_controller import RobotControllerAgent


async def main():
    print("\n🤖 Style.re AI Robotics OPC — Pick & Place Demo\n")

    agent = RobotControllerAgent(sim=True)

    # Task 1: Pick a package from shelf
    task_id = await agent.receive_task({
        "task_id": "task-001",
        "type": "pick",
        "target": {"coordinates": [10.0, 5.0, 2.0], "item": "Gucci Bag SKU-4421"},
        "priority": 2
    })
    print(f"✅ Task queued: {task_id}")

    # Task 2: Place it in delivery zone
    task_id2 = await agent.receive_task({
        "task_id": "task-002",
        "type": "place",
        "target": {"coordinates": [0.0, 0.0, 0.5], "zone": "dispatch-A"},
        "priority": 2
    })
    print(f"✅ Task queued: {task_id2}")

    # Task 3: Deliver
    await agent.receive_task({
        "task_id": "task-003",
        "type": "deliver",
        "target": {
            "package_id": "PKG-8819",
            "address": "1234 Oak Cliff Blvd, Dallas TX 75203",
            "coordinates": [50.0, 30.0]
        },
        "priority": 3
    })

    print(f"\n📊 Agent status: {agent.status()}\n")

    # Execute all tasks
    while True:
        result = await agent.execute_next()
        print(f"  → {result}")
        if result.get("status") == "idle":
            break

    print(f"\n✅ Final status: {agent.status()}")


if __name__ == "__main__":
    asyncio.run(main())
