# Agent Interaction Guide

## How Customers Talk to the Agent

The RetailShopperAgent understands natural language requests.

### Example Requests

```
"Find me a size M black hoodie under $300"
"I need a blue dress size L for a dinner date"
"What Saint Laurent bags do you have under $2000?"
"Get me something casual for the weekend, I wear medium"
```

### Supported Parameters (auto-detected)

| Parameter | Examples |
|-----------|---------|
| Size | "size M", "medium", "L", "XL" |
| Color | "black", "blue", "beige", "white" |
| Category | "hoodie", "dress", "blazer", "bag", "sneaker" |
| Budget | "$300", "under 500", "less than $700" |
| Brand | "Saint Laurent", "Gucci", "Prada" |

### OpenClaw Skill Flow

1. Agent receives message
2. `search_inventory` skill queries store DB
3. Results ranked by customer style profile
4. Top 3 items selected → pick list generated
5. `dispatch_robot` skill sends pick list to robot
6. After delivery: `handle_return` skill processes keeps/returns
