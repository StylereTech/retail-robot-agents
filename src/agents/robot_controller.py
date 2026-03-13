"""
Robot Controller Agent — OpenClaw-compatible
Controls physical or simulated robot hardware via LLM-driven planning.
"""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

from utils.config import Config
from utils.logger import get_logger
from hardware.lobster_box_sim import LobsterBoxSim

logger = get_logger(__name__)


@dataclass
class Task:
    task_id: str
    type: str  # "pick", "place", "navigate", "deliver"
    target: dict
    priority: int = 1
    status: str = "pending"


class RobotControllerAgent:
    """
    OpenClaw-compatible agent for robot control.
    Receives tasks from the orchestrator, plans actions, executes on hardware.
    """

    def __init__(self, config: Optional[Config] = None, sim: bool = True):
        self.config = config or Config()
        self.sim = sim
        self.hardware = LobsterBoxSim() if sim else None
        self.task_queue: list[Task] = []
        logger.info("RobotControllerAgent initialized (sim=%s)", sim)

    async def receive_task(self, task: dict) -> str:
        """Accept a task from OpenClaw orchestrator."""
        t = Task(**task)
        self.task_queue.append(t)
        logger.info("Task received: %s (type=%s)", t.task_id, t.type)
        return t.task_id

    async def execute_next(self) -> dict:
        """Execute the next pending task."""
        pending = [t for t in self.task_queue if t.status == "pending"]
        if not pending:
            return {"status": "idle", "message": "No pending tasks"}

        task = sorted(pending, key=lambda t: t.priority, reverse=True)[0]
        task.status = "running"
        logger.info("Executing task %s...", task.task_id)

        try:
            if task.type == "pick":
                result = await self._pick(task.target)
            elif task.type == "place":
                result = await self._place(task.target)
            elif task.type == "navigate":
                result = await self._navigate(task.target)
            elif task.type == "deliver":
                result = await self._deliver(task.target)
            else:
                result = {"error": f"Unknown task type: {task.type}"}

            task.status = "completed"
            return {"task_id": task.task_id, "status": "completed", "result": result}

        except Exception as e:
            task.status = "failed"
            logger.error("Task %s failed: %s", task.task_id, e)
            return {"task_id": task.task_id, "status": "failed", "error": str(e)}

    async def _pick(self, target: dict) -> dict:
        coords = target.get("coordinates", [0, 0, 0])
        if self.hardware:
            await self.hardware.move_to(coords)
            await self.hardware.grip()
        return {"action": "pick", "coordinates": coords, "success": True}

    async def _place(self, target: dict) -> dict:
        coords = target.get("coordinates", [0, 0, 0])
        if self.hardware:
            await self.hardware.move_to(coords)
            await self.hardware.release()
        return {"action": "place", "coordinates": coords, "success": True}

    async def _navigate(self, target: dict) -> dict:
        waypoints = target.get("waypoints", [])
        for wp in waypoints:
            if self.hardware:
                await self.hardware.navigate_to(wp)
        return {"action": "navigate", "waypoints_completed": len(waypoints)}

    async def _deliver(self, target: dict) -> dict:
        address = target.get("address", "")
        package_id = target.get("package_id", "")
        logger.info("Delivering package %s to %s", package_id, address)
        await self._navigate({"waypoints": [target.get("coordinates", [0, 0])]})
        return {"action": "deliver", "package_id": package_id, "address": address, "success": True}

    def status(self) -> dict:
        return {
            "total_tasks": len(self.task_queue),
            "pending": len([t for t in self.task_queue if t.status == "pending"]),
            "running": len([t for t in self.task_queue if t.status == "running"]),
            "completed": len([t for t in self.task_queue if t.status == "completed"]),
            "failed": len([t for t in self.task_queue if t.status == "failed"]),
        }
