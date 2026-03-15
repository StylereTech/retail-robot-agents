# Setup Guide

## Prerequisites

- Python 3.10+
- Git
- Docker (optional)
- ROS2 Humble (optional, real hardware only)

## Installation

```bash
git clone https://github.com/StylereTech/Style.re_AI-robotics-OPC.git
cd Style.re_AI-robotics-OPC
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment

```bash
cp .env.example .env
# Edit .env with your OpenClaw API key
```

## Run Demo

```bash
python examples/simple_robot_arm.py
```
