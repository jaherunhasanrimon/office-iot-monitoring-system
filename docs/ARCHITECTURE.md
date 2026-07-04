# Architecture Reference

See the full system architecture in the project root [`README.md`](../README.md).

## Component Summary

| Component | Technology | Port |
|---|---|---|
| Backend API + Simulator | Python Flask + APScheduler | 5000 |
| Real-time layer | Flask-SocketIO | 5000 (same) |
| Database | MySQL 8.x | 3306 |
| Web Dashboard | React + Vite | 5173 |
| Discord Bot | discord.py 2.x | — |

## Data Flow

```
APScheduler (tick)
  → simulator.py (toggles devices in MySQL)
  → alert_engine.py (evaluates Rule A + Rule B)
  → Flask-SocketIO (broadcasts device_update / alert_created)
  → React dashboard (re-renders, no page refresh)
  → Flask REST API (Discord bot reads on demand)
```

## Alert Rules

| Rule | Trigger | Type |
|---|---|---|
| A | Any device ON outside 9 AM–5 PM | `after_hours` |
| B | ALL devices in a room ON > 2 hrs continuously | `prolonged_room_on` |
