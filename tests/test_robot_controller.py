"""Basic unit tests for RobotControllerAgent."""
import asyncio
import pytest
import sys
sys.path.insert(0, "src")

from agents.robot_controller import RobotControllerAgent


@pytest.mark.asyncio
async def test_receive_task():
    agent = RobotControllerAgent(sim=True)
    task_id = await agent.receive_task({
        "task_id": "test-001",
        "type": "pick",
        "target": {"coordinates": [1, 2, 3]},
    })
    assert task_id == "test-001"
    assert agent.status()["pending"] == 1


@pytest.mark.asyncio
async def test_execute_pick():
    agent = RobotControllerAgent(sim=True)
    await agent.receive_task({
        "task_id": "test-002",
        "type": "pick",
        "target": {"coordinates": [0, 0, 1]},
    })
    result = await agent.execute_next()
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_idle_when_no_tasks():
    agent = RobotControllerAgent(sim=True)
    result = await agent.execute_next()
    assert result["status"] == "idle"
