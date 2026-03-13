# Style.re AI Robotics — OPC

> **AI-powered robotic agent system for last-mile delivery operations.**
> OpenClaw-compatible · ROS-ready · Lobster Box simulation included

![Architecture](assets/architecture_diagram.png)

---

## What Is This?

Style.re AI Robotics OPC is an open-source agent framework that bridges large language models (LLMs) with physical robotics hardware for real-world last-mile delivery automation. Built on [OpenClaw](https://openclaw.ai), it enables AI agents to plan, coordinate, and execute pick-and-place, warehouse navigation, and delivery dispatch tasks — in simulation or on real hardware.

**Use cases:**
- 🤖 Autonomous warehouse picking for fashion/retail fulfillment
- 🚚 Last-mile delivery robot coordination
- 🦾 Lobster Box robotic arm simulation + real hardware integration
- 🧠 Multi-agent swarm coordination via OpenClaw

---

## Quick Start

```bash
git clone https://github.com/StylereTech/Style.re_AI-robotics-OPC.git
cd Style.re_AI-robotics-OPC
pip install -r requirements.txt

# Run the simple robot arm demo
python examples/simple_robot_arm.py

# Run with Docker
docker build -t opc-robotics docker/
docker run --rm opc-robotics
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   OpenClaw Agent Layer               │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────┐  │
│   │ Robot Ctrl  │  │  Task Planner│  │  Skills  │  │
│   │   Agent     │  │    Agent     │  │  (YAML)  │  │
│   └──────┬──────┘  └──────┬───────┘  └────┬─────┘  │
└──────────┼────────────────┼───────────────┼─────────┘
           │                │               │
┌──────────▼────────────────▼───────────────▼─────────┐
│                   Hardware Bridge Layer               │
│   ┌─────────────┐         ┌──────────────────────┐  │
│   │  ROS Bridge │         │  Lobster Box Sim/HW  │  │
│   │ (ros_bridge)│         │  (lobster_box_sim)   │  │
│   └─────────────┘         └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
           │
┌──────────▼──────────┐
│   Physical Hardware  │
│   Robot Arm / Nav    │
└─────────────────────┘
```

---

## Project Structure

```
Style.re_AI-robotics-OPC/
├── README.md
├── LICENSE                  # MIT
├── .gitignore
├── requirements.txt
├── docs/
│   ├── architecture.md      # Deep-dive system design
│   ├── setup.md             # Hardware + software setup
│   ├── demo-guide.md        # Step-by-step demo walkthrough
│   └── zh/                  # Chinese translations
├── src/
│   ├── agents/
│   │   ├── robot_controller.py   # Main OpenClaw-compatible agent
│   │   └── skills/              # Custom skills (YAML + Python)
│   ├── hardware/
│   │   ├── ros_bridge.py        # ROS2 integration
│   │   └── lobster_box_sim.py   # Lobster Box simulation
│   └── utils/
│       ├── logger.py
│       └── config.py
├── examples/
│   ├── simple_robot_arm.py         # Pick-and-place demo
│   └── warehouse_nav_demo.ipynb    # Jupyter: embodied nav task
├── tests/
├── docker/
│   └── Dockerfile
└── assets/
    ├── architecture_diagram.png
    └── demo.gif
```

---

## Key Features

| Feature | Status |
|---------|--------|
| OpenClaw agent integration | ✅ Ready |
| ROS2 bridge | ✅ Ready |
| Lobster Box simulation | ✅ Ready |
| Pick-and-place demo | ✅ Ready |
| Warehouse navigation | 🔄 In progress |
| Multi-agent swarm | 🔄 In progress |
| Real hardware support | 📅 Planned |

---

## Requirements

- Python 3.10+
- OpenClaw (latest)
- ROS2 Humble (optional, for real hardware)
- Docker (optional)

---

## Contributing

PRs welcome. See [docs/setup.md](docs/setup.md) for dev setup.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [StylereTech](https://github.com/StylereTech) · Powered by [Stowry](https://stylere.app)*
