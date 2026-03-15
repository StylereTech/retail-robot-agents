"""Configuration loader."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENCLAW_API_KEY: str = os.getenv("OPENCLAW_API_KEY", "")
    ROBOT_SIM_MODE: bool = os.getenv("ROBOT_SIM_MODE", "true").lower() == "true"
    ROS_ENABLED: bool = os.getenv("ROS_ENABLED", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
