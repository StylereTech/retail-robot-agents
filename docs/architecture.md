# Architecture

## Overview

Style.re AI Robotics OPC is a three-layer system:

1. **OpenClaw Agent Layer** — LLM-driven task planning and coordination
2. **Hardware Bridge Layer** — ROS2 and direct hardware interfaces  
3. **Physical Hardware Layer** — Robot arms, mobile bases, sensors

## Data Flow

```
User/System Request
       ↓
OpenClaw Orchestrator (007 Agent)
       ↓
RobotControllerAgent.receive_task()
       ↓
Task Planner → Action Sequence
       ↓
Hardware Bridge (ROS2 / Direct)
       ↓
Physical Robot
```

## Agent Skills

Skills are YAML-defined capabilities that OpenClaw loads at runtime:
- `pick_item` — Identify and grasp a SKU from shelf
- `place_item` — Place item in designated zone
- `navigate` — Move to waypoint via Nav2
- `deliver` — End-to-end delivery execution

## Simulation vs Real Hardware

Set `ROBOT_SIM_MODE=true` in `.env` for simulation (default).  
Set `ROS_ENABLED=true` + install ROS2 Humble for real hardware.
