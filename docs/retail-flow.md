# Retail Flow — Customer to Door

## Full System Flow

```
Customer (App)
    │ "Find me a M black hoodie under $700"
    ▼
RetailShopperAgent
    ├── search_inventory skill
    ├── rank_by_preference
    └── generate_pick_list
    │
    ▼ Agent-Robot Protocol (ARP)
RobotControllerAgent
    ├── receive pick_list
    ├── navigate to shelf locations
    └── pick items with Lobster Box arm
    │
    ▼
DeliveryCoordinatorAgent
    ├── dispatch driver (DoorDash Drive / Style.re)
    └── track delivery
    │
    ▼
Customer (at home)
    ├── try on
    ├── keep → Stripe charge
    └── return → ReturnHandler schedules pickup
    │
    ▼
ReturnHandler
    ├── pickup scheduled
    └── inventory restocked
```

## Timing (Simulated)

| Step | Duration |
|------|----------|
| Agent search + curation | < 2 seconds |
| Robot pick (sim) | ~3 seconds/item |
| Driver dispatch | < 1 minute |
| Delivery (Dallas) | 30-45 minutes |
| Return pickup | Within 2 hours |
