# 零售流程 — 从顾客到送达

## 完整系统流程

```
顾客（App）
    │ "帮我找一件 M 码黑色卫衣，700 元以内"
    ▼
RetailShopperAgent（零售购物智能体）
    ├── search_inventory 技能（搜索库存）
    ├── 按偏好排序
    └── 生成拣货清单
    │
    ▼ 智能体-机器人协议 (ARP)
RobotControllerAgent（机器人控制智能体）
    ├── 接收拣货清单
    ├── 导航至货架位置
    └── Lobster Box 机械臂抓取商品
    │
    ▼
DeliveryCoordinatorAgent（配送协调智能体）
    ├── 派单（DoorDash Drive / Style.re）
    └── 实时追踪
    │
    ▼
顾客（在家试穿）
    ├── 保留 → Stripe 扣款
    └── 退货 → ReturnHandler 安排取件
    │
    ▼
ReturnHandler（退货处理）
    ├── 安排取件
    └── 库存补货
```
