"""
ROS2 Bridge — connects OpenClaw agent to ROS2 ecosystem.
Requires ROS2 Humble and rclpy installed.
"""
from __future__ import annotations
import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist, Pose
    from std_msgs.msg import String
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    logger.warning("ROS2 not available — using stub mode")


class ROSBridge:
    """
    Bridges OpenClaw agent commands to ROS2 topics/services.
    Falls back to stub mode if ROS2 is not installed.
    """

    def __init__(self, node_name: str = "opc_agent_bridge"):
        self.node_name = node_name
        self.node = None
        self._initialized = False

        if ROS_AVAILABLE:
            rclpy.init()
            self.node = rclpy.create_node(node_name)
            self._cmd_vel_pub = self.node.create_publisher(Twist, "/cmd_vel", 10)
            self._status_sub = self.node.create_subscription(
                String, "/robot_status", self._on_status, 10
            )
            self._initialized = True
            logger.info("ROS2 bridge initialized (node=%s)", node_name)
        else:
            logger.info("ROS2 bridge running in STUB mode")

    def _on_status(self, msg):
        logger.debug("Robot status: %s", msg.data)

    async def send_velocity(self, linear: float, angular: float) -> bool:
        if not ROS_AVAILABLE or not self.node:
            logger.debug("[STUB] cmd_vel: linear=%.2f angular=%.2f", linear, angular)
            return True
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self._cmd_vel_pub.publish(twist)
        return True

    async def navigate_to_pose(self, x: float, y: float, theta: float = 0.0) -> bool:
        logger.info("Navigate to pose: x=%.2f y=%.2f theta=%.2f", x, y, theta)
        if not ROS_AVAILABLE:
            await asyncio.sleep(1.0)  # simulate travel
            return True
        # Real implementation would use Nav2 action client
        return True

    def shutdown(self):
        if ROS_AVAILABLE and self.node:
            self.node.destroy_node()
            rclpy.shutdown()
