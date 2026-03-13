"""
Lobster Box Simulation
Simulates the Lobster Box robotic arm for testing without physical hardware.
"""
from __future__ import annotations
import asyncio
import math
from utils.logger import get_logger

logger = get_logger(__name__)

JOINT_SPEED = 0.05  # seconds per degree of movement


class LobsterBoxSim:
    """
    Simulated Lobster Box robotic arm.
    Provides async interface matching the real hardware API.
    """

    def __init__(self):
        self.position = [0.0, 0.0, 0.0]  # x, y, z
        self.gripper_open = True
        self.joints = [0.0] * 6  # 6-DOF arm
        logger.info("LobsterBoxSim initialized at home position")

    async def move_to(self, coordinates: list[float], speed: float = 1.0) -> bool:
        x, y, z = coordinates
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, [x, y, z])))
        travel_time = (distance / 100) / speed  # simulate travel time
        logger.debug("Moving to [%.2f, %.2f, %.2f] (%.2fs)", x, y, z, travel_time)
        await asyncio.sleep(min(travel_time, 2.0))  # cap at 2s for sim
        self.position = [x, y, z]
        return True

    async def grip(self) -> bool:
        logger.debug("Gripper: CLOSE")
        await asyncio.sleep(0.3)
        self.gripper_open = False
        return True

    async def release(self) -> bool:
        logger.debug("Gripper: OPEN")
        await asyncio.sleep(0.3)
        self.gripper_open = True
        return True

    async def navigate_to(self, waypoint: list[float]) -> bool:
        return await self.move_to(waypoint)

    async def home(self) -> bool:
        return await self.move_to([0.0, 0.0, 0.0])

    def get_state(self) -> dict:
        return {
            "position": self.position,
            "gripper_open": self.gripper_open,
            "joints": self.joints,
        }
