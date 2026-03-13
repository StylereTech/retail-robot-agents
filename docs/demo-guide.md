# Demo Guide — Lobster Box / Real Robot

## Simulation Demo (No Hardware)

1. Clone the repo and install requirements
2. Run: `python examples/simple_robot_arm.py`
3. Watch the agent queue and execute pick/place/deliver tasks

## Real Hardware (Lobster Box)

1. Connect Lobster Box via USB/Ethernet
2. Set `ROBOT_SIM_MODE=false` in `.env`
3. Calibrate home position: `python src/hardware/lobster_box_sim.py --calibrate`
4. Run: `python examples/simple_robot_arm.py`

## ROS2 Integration

1. Install ROS2 Humble: https://docs.ros.org/en/humble/
2. Set `ROS_ENABLED=true` in `.env`
3. Launch ROS2: `ros2 launch opc_bringup robot.launch.py`
4. Run agent: `python src/agents/robot_controller.py`
