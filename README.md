# Retail Robot Agents 🦞

> **Autonomous retail delivery & in-store pickup via OpenClaw agents + robots.**
> Agent shops. Robot picks. We deliver. No humans needed.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/Powered%20by-OpenClaw-blue)](https://openclaw.ai)
[![ROS2](https://img.shields.io/badge/ROS2-Humble-green)](https://docs.ros.org/en/humble/)

---

## No-Humans Retail Revolution

**OpenClaw agents + robots handle last-mile delivery, in-store pickup, curbside handoff, and returns.**

Customers shop via app — agents pick, robots deliver. No store associates. No checkout lines. No delays.

```
Customer: "Find me a size M black hoodie under $300"
      ↓
OpenClaw Agent searches live store inventory
      ↓
Agent dispatches robot with pick list
      ↓
Robot navigates store → grabs item from shelf
      ↓
Curbside or home delivery via Style.re network
      ↓
Customer tries on at home
      ↓
Keep it → pay.   Don't love it → one tap, we pick it up.
```

> **Built for Shenzhen's AI infrastructure subsidies**: free compute for agent training, Lobster Box edge hardware, and Longgang District's 2M RMB grants for digital employees in transport & retail.

---

## Demo Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 CUSTOMER                                                     │
│  "Hey, find me a blue dress size L for under $400"              │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  🧠 OPENCLAW RETAIL AGENT                                        │
│  retail_shopper.py                                               │
│  ├── search_inventory skill → finds 3 matching items            │
│  ├── ranks by customer style profile                            │
│  └── generates pick list → dispatches to robot                  │
└────────────────────┬────────────────────────────────────────────┘
                     │  Agent-Robot Protocol (ARP)
┌────────────────────▼────────────────────────────────────────────┐
│  🤖 IN-STORE ROBOT                                               │
│  in_store_picker.py + robot_delivery_bot.py                     │
│  ├── navigates to Aisle W4, Rack 3, Position 7                  │
│  ├── grabs item with Lobster Box arm                            │
│  └── moves to dispatch zone                                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  🚚 STYLE.RE LAST-MILE DELIVERY                                  │
│  delivery_coordinator.py                                         │
│  ├── Driver dispatched via DoorDash Drive API                   │
│  ├── Real-time tracking to customer                             │
│  └── Return pickup scheduled if needed                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Shenzhen / Longgang Alignment

| Subsidy Program | How We Qualify |
|----------------|---------------|
| **Longgang AI Digital Employee Grant** (2M RMB) | Our OpenClaw agents = digital employees in retail/transport |
| **Low-Altitude Economy Subsidies** | Delivery routing + traffic data integration |
| **Lobster Box Hardware Program** | Native Lobster Box arm integration (sim + real) |
| **Free AI Compute (Training)** | Agent training on Shenzhen retail datasets |
| **Embodied AI Pilot Program** | In-store robot = perfect embodied AI deployment |

> Compatible with Longgang's low-altitude/traffic data subsidies — agents train on real city flows.
> Uses Lobster Box edge compute — simulation + real hardware integration included.
> OPC-first: One founder, scalable to zero-human retail across all 50 states + China.

---

## Project Structure

```
retail-robot-agents/
├── README.md                          # This file
├── README-zh.md                       # 中文版本 (Chinese)
├── LICENSE
├── requirements.txt
├── docs/
│   ├── retail-flow.md                 # Full system flow diagram
│   ├── agent-interaction-guide.md     # How customers talk to agents
│   └── zh/                            # Chinese documentation
│       ├── retail-flow-zh.md
│       └── agent-guide-zh.md
├── src/
│   ├── agents/
│   │   ├── retail_shopper.py          # Browses inventory, curates picks
│   │   ├── delivery_coordinator.py    # Orchestrates dispatch + returns
│   │   └── skills/                    # OpenClaw YAML skill definitions
│   │       ├── search_inventory.yaml
│   │       ├── dispatch_robot.yaml
│   │       └── handle_return.yaml
│   ├── hardware/
│   │   ├── robot_delivery_bot.py      # ROS2: navigation + curbside drop
│   │   ├── in_store_picker.py         # Shelf navigation + arm pickup
│   │   └── lobster_box_sim.py         # Lobster Box simulation
│   └── retail_utils/
│       ├── inventory_api.py           # Store inventory interface
│       └── return_handler.py          # Return logic + robot dispatch
├── examples/
│   ├── curbside_pickup_demo.py        # Agent → Robot → Curbside handoff
│   └── try_on_return_sim.ipynb        # Keep/return flow simulation
├── tests/
│   └── test_retail_agent.py
├── docker/
│   └── Dockerfile
└── assets/
    ├── retail_flow_diagram.png
    └── demo.gif
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent orchestration | [OpenClaw](https://openclaw.ai) |
| Agent skills | YAML skill definitions (`search_inventory`, `dispatch_robot`, `handle_return`) |
| Robot OS | ROS2 Humble + Gazebo simulation |
| Robot hardware | Lobster Box arm + mobile base |
| Vision (roadmap) | YOLO / CLIP — "find black hoodie on shelf" |
| Last-mile delivery | [Style.re](https://stylere.app) + DoorDash Drive API |
| Inventory | MongoDB (live) / JSON mock (demo) |
| Returns | Automated via delivery_coordinator agent |

---

## Quick Start

```bash
git clone https://github.com/StylereTech/retail-robot-agents.git
cd retail-robot-agents
pip install -r requirements.txt

# Run curbside pickup demo (no hardware needed)
python examples/curbside_pickup_demo.py
```

---

## Why This Wins Funding

- **Embodied + Agent + Retail** = perfect for "AI + manufacturing/transport/medical" investment focus
- **Returns loop** = real unit economics (reduce waste, build trust, close the loop)
- **No humans = labor cost killer** — scales to any store without hiring
- **Try-before-you-buy** = higher conversion, lower friction than e-commerce
- **Public repo + runnable demo** = instant proof of execution, not just talk
- **China-ready**: Chinese README, Lobster Box native, Longgang grant-aligned

---

## Roadmap

| Phase | Milestone | ETA |
|-------|-----------|-----|
| ✅ 1 | Agent personal shopper + style curation | Done |
| ✅ 2 | Agent-Robot Protocol (ARP) | Done |
| ✅ 3 | Lobster Box simulation | Done |
| ✅ 4 | ROS2 integration | Done |
| 🔄 5 | Style.re delivery integration | Q2 2026 |
| 🔄 6 | Try-before-you-buy + automated returns | Q2 2026 |
| 📅 7 | YOLO/CLIP visual shelf navigation | Q3 2026 |
| 📅 8 | Shenzhen pilot — Longgang retail partner | Q3 2026 |
| 📅 9 | Multi-store robot fleet management | Q4 2026 |

---

*Built by [StylereTech](https://github.com/StylereTech) / Stowry · Dallas TX + Shenzhen*
*[中文版本 →](README-zh.md)*

---

## Demo

A full live demo system — FastAPI backend + Next.js dashboard + real MongoDB inventory.

### Quick Start

**Prerequisites:** Python 3.11+, Node.js 18+, npm

#### 1. Install Python dependencies

```bash
pip install fastapi uvicorn websockets pymongo python-multipart loguru pyyaml
```

#### 2. Start the backend

```bash
cd /path/to/retail-robot-agents
uvicorn demo.server.main:app --reload --port 8000
```

Or from the server directory:

```bash
cd demo/server
uvicorn main:app --reload --port 8000
```

#### 3. Start the frontend

```bash
cd demo/frontend
npm install
npm run dev
# Open http://localhost:3000
```

#### 4. Run with Docker Compose

```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Demo Flow

1. Open **http://localhost:3000**
2. Click **▶ Run Demo**
3. Watch the 3-panel dashboard:
   - **Left** — Live agent activity feed (StyleAgent → RobotControllerAgent → Dispatch)
   - **Center** — Animated robot arm picking luxury items
   - **Right** — Order summary with real product data, running total, DoorDash-style tracking

### Demo Customer Profile

```json
{
  "name": "Alexandra Chen",
  "occasion": "business dinner",
  "budget_max": 2500,
  "preferred_brands": ["Saint Laurent", "Prada", "Bottega Veneta"],
  "style_tags": ["minimalist", "luxury", "business"]
}
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/inventory` | Fetch luxury products from MongoDB |
| `POST` | `/api/demo/run` | Trigger demo run (accepts customer profile JSON) |
| `WS` | `/ws/demo` | Stream live agent events |

### WebSocket Event Format

```json
{
  "type": "agent|robot|dispatch|complete|error",
  "message": "Human-readable description",
  "data": {},
  "timestamp": "2026-03-15T12:00:00Z"
}
```
