# Project Blueprint: "Lights, Fans, Discord" — Office IoT Monitoring System
**Techathon Nationals & Rover Summit — Preliminary Round**

---

## 1. Executive Summary

### The problem, in plain language
A small office loses money because people forget to turn off lights and fans before leaving. Nobody notices until the electricity bill arrives. The boss wants a way to **see, at a glance, what's on and what's burning power**, from two places: a **web dashboard** (visual, live) and a **Discord bot** (quick, text-based, works from a phone).

Since there's no real hardware available for the hackathon, the system is a **simulation**: fake devices "report" their state to a backend, and both the dashboard and the bot read from that same backend.

### The real-world problem being solved
This is a classic **IoT + energy-monitoring** problem, minus the actual IoT hardware:
- **Energy waste from human forgetfulness** (devices left on).
- **Lack of visibility** — no single place to see device states across rooms.
- **Lack of accountability/alerting** — nothing flags waste as it happens.
- **Access friction** — a dashboard requires opening a browser; a chat bot is faster for a quick check.

The underlying skill being tested isn't really "build a smart plug" — it's **can you design a clean multi-client architecture (web + chat) sharing one real-time backend, and can you fake hardware convincingly enough that the concept is believable?**

---

## 2. Feature Analysis

### 2.1 Core (Must Have) — directly required by the brief, tied to graded criteria

| # | Feature | Why it's core |
|---|---|---|
| 1 | Simulated data layer for 15 devices (6 fans, 9 lights across 3 rooms) with status, wattage, room, last-changed timestamp | Explicitly required; feeds everything else |
| 2 | Backend API that is the single source of truth | Explicit "Architecture Requirement" |
| 3 | Real-time web dashboard: live device status panel, per-room breakdown | 20% of grade |
| 4 | Live power consumption meter (total + per-room) | Explicitly required |
| 5 | Active Alerts Panel (after-hours devices, room on >2hrs continuously) | Explicitly required, timestamped |
| 6 | No-refresh live updates on dashboard (WebSocket/SSE/polling) | Explicit clarification #3 |
| 7 | Discord bot with `!status`, `!room <name>`, `!usage` | Explicit minimum commands, 10% of grade |
| 8 | Bot answers from real simulated data (not hardcoded/random) | Explicit requirement |
| 9 | High-level system diagram (no Mermaid) | 15% of grade |
| 10 | Hardware/electrical schematic in Wokwi or Tinkercad (1 room is enough) | 15% of grade |
| 11 | Public repo with README (setup instructions for backend, dashboard, bot) | Explicit deliverable |
| 12 | Video demo (≤3 min) | Explicit deliverable |

### 2.2 Important (Should Have) — strongly implied, raises quality/score but not explicitly mandatory

| # | Feature | Why it matters |
|---|---|---|
| 1 | Humanized/friendly bot responses (LLM-generated phrasing) | Explicitly "strongly encouraged"; affects UX perception |
| 2 | Dynamic simulator that changes state over time (not static JSON) | Explicit requirement — "dashboard always has something live to show" |
| 3 | Clean, well-organized codebase with meaningful commit history | 15% of grade ("Well structured and documented Codebase, Commits") |
| 4 | Per-device identification (e.g., "Fan 1", "Light 3") | Explicit requirement |
| 5 | Today's estimated kWh usage calculation | Needed for `!usage` sample output ("4.2 kWh") |
| 6 | Office-hours logic (9 AM–5 PM) baked into alert engine | Needed for after-hours alert |

### 2.3 Optional (Nice to Have / Bonus)

| # | Feature | Notes |
|---|---|---|
| 1 | Top-view office layout on dashboard with glowing lights / animated fans | Explicitly called out as **bonus points** |
| 2 | Bot proactively posts alerts to a Discord channel unprompted | Explicitly called out as **bonus** |
| 3 | Current-sensing concept in the schematic (not just on/off) | Explicitly "optionally sensing current draw" |
| 4 | Historical usage charts (hourly/daily trend) | Implied by "today's estimated usage" |
| 5 | Manual device toggle from dashboard/bot (control, not just monitor) | Not requested, but a natural judge-pleaser if time allows |

### 2.4 Hidden / Implied Requirements (easy to miss)

- **Consistency guarantee**: dashboard and bot must never disagree — this means *no separate mock data per client*; both must call the same backend/API.
- **Timestamps everywhere**: device `last_changed`, alerts, and usage figures all need real timestamps, not just numbers — judges can spot fake static demos.
- **Office-hours-aware logic**: "after office hours" requires the system to know current time vs. a fixed 9–5 window — this is actual logic, not just a UI label.
- **"All devices in a room on >2hrs continuously"** requires tracking *continuous on-duration per device*, which means your data model needs an "on since" timestamp, not just current status.
- **Simulator must persist state across time**, not regenerate randomly every request (otherwise "last changed" and "continuous on-time" become meaningless).
- **The circuit schematic must "make physical sense"** — you can't just drop LEDs on a breadboard; you need a plausible sensing approach (relay + digital read, or current sensor) even though it's conceptual.
- **README must cover 3 separate run targets** (backend, dashboard, bot) — a single global "npm start" without clear separation will read as poorly documented even if the code is fine.
- **Grading rewards breadth over depth in specific ratios** — schematic (15%) and system diagram (15%) are worth as much as the dashboard's real-time behavior (20%), so this is *not* purely a coding contest; documentation/design artifacts matter as much as working software.

---

## 3. Functional Requirements

### 3.1 User actions (the "boss" / any dashboard or Discord user)

| Action | Interface | Result |
|---|---|---|
| View all device states | Dashboard | Live-updating panel grouped by room |
| View total & per-room power draw | Dashboard | Live wattage numbers |
| View active alerts | Dashboard | Timestamped list of anomalies |
| View office layout visually (bonus) | Dashboard | Top-view SVG/graphic with device states reflected |
| Run `!status` | Discord | Full office summary, per room |
| Run `!room <name>` | Discord | Summary for one room |
| Run `!usage` | Discord | Current wattage + today's estimated kWh |
| Receive proactive alert (bonus) | Discord | Bot posts unprompted when anomaly triggers |

### 3.2 System / background actions (no human trigger)

| Action | Trigger | Result |
|---|---|---|
| Simulate device state changes | Timer/interval (e.g., every 10–60s) | Random subset of devices toggle on/off; `last_changed` updates |
| Recalculate total & per-room wattage | On every state change / on interval | Backend aggregate updates, pushed to dashboard |
| Evaluate alert rules | On interval or on state change | New alerts created if: (a) any device ON outside 9 AM–5 PM, (b) any room has *all* devices ON continuously for >2 hrs |
| Push live update to dashboard | On any state/alert change | WebSocket/SSE event broadcast |
| Log usage snapshot for kWh estimate | On interval (e.g., every 5 min) | Append to usage log, used to compute "today's estimated usage" |
| Bot posts to alert channel (bonus) | New alert created | Discord bot sends formatted message to configured channel |

### 3.3 Core workflows

**Workflow A — Live Dashboard Update**
```
Simulator tick → Device state changes in DB/store
              → Backend recalculates room + total wattage
              → Backend evaluates alert rules
              → Backend emits event over WebSocket/SSE
              → Dashboard client receives event → re-renders panel (no refresh)
```

**Workflow B — Discord Query**
```
User types !status in Discord
   → Bot receives command
   → Bot calls Backend API (GET /api/devices or /api/summary)
   → Bot formats response (optionally via LLM for friendly tone)
   → Bot replies in channel
```

**Workflow C — Alert Lifecycle**
```
Alert condition detected (rule engine)
   → Alert record created (type, room/device, message, timestamp)
   → Dashboard Alerts Panel updates via live channel
   → (Bonus) Bot posts proactively to designated channel
   → Alert marked resolved when condition clears (optional but good practice)
```

---

## 4. Non-Functional Requirements

### Performance
- Dashboard updates should feel "live" — target **under 2–3 seconds** from simulated state change to UI update.
- Simulator tick interval should be tunable (suggest 10–30s) — fast enough to demo well in a 3-minute video, slow enough to look realistic.
- API responses for Discord commands should return in **under 1 second** under normal load (single backend, low device count — this is easily achievable).

### Security
- No physical hardware/secrets to protect, but still:
  - Keep Discord bot token and any LLM API keys in environment variables, **never committed to the repo**.
  - Add `.env` to `.gitignore` from day one.
  - If you add a device "control" (toggle) endpoint, don't expose it unauthenticated on a public demo URL — at minimum use a shared secret header.

### Scalability
- Not a major concern at 15 devices / 3 rooms, but design the data model so **adding a room or device type doesn't require code changes** (e.g., devices table with `room` and `type` fields, not hardcoded room-specific logic).
- Real-time layer (WebSocket/SSE) should support multiple simultaneous dashboard viewers without duplicating simulator logic per client.

### Reliability
- Simulator state must be the **single source of truth** in memory or a lightweight DB (SQLite/JSON file) — restarting the backend shouldn't silently reset in a way that breaks demo continuity mid-presentation.
- Discord bot should reconnect gracefully if it loses connection (library default behavior in discord.js/discord.py is usually sufficient — just don't crash the process on a single failed API call).

### UI/UX
- Dashboard must clearly separate: **device status**, **power meter**, **alerts** — three distinct visual zones, not one long list.
- Use color/iconography consistently (e.g., amber glow = light on, spinning icon = fan on, red badge = alert).
- Discord responses must read as natural sentences, not raw JSON dumps — this is explicitly graded ("the boss hates robotic data dumps").

### Accessibility
- Not explicitly graded, but low-effort wins: sufficient color contrast for on/off indicators (don't rely on color alone — pair with icon/text), reasonably sized touch targets if dashboard is viewed on mobile during the demo.

---

## 5. System Design

### 5.1 Suggested Architecture

```
┌─────────────────────┐
│  Device Simulator    │  (interval-based state generator)
│  (in backend process)│
└──────────┬───────────┘
           │ writes/reads
           ▼
┌─────────────────────┐        ┌────────────────────┐
│   Data Store          │◄──────►│  Alert Rule Engine  │
│ (SQLite / in-memory)  │        │ (evaluates on tick) │
└──────────┬───────────┘        └────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│               Backend API (single source        │
│         of truth) — REST + WebSocket/SSE          │
└───────┬─────────────────────────┬───────────────┘
        │ REST (poll on command)  │ WebSocket/SSE (live push)
        ▼                          ▼
┌───────────────┐          ┌─────────────────────┐
│  Discord Bot     │          │   Web Dashboard        │
│ (discord.js/py)  │          │ (React/HTML+JS)        │
└───────┬───────┘          └─────────────────────┘
        │
        ▼
   Discord Server (boss + team)
```

**Key design decision**: the Discord bot uses plain REST calls (it only needs data *on demand*, per command), while the dashboard uses a persistent WebSocket/SSE connection (it needs *continuous* live updates). Both hit the same backend — satisfying the "single source of truth" requirement without duplicating logic.

### 5.2 Modules

| Module | Responsibility |
|---|---|
| `simulator` | Generates/mutates device state over time |
| `alert-engine` | Evaluates rules against current state, produces alert records |
| `api` | REST endpoints for devices, rooms, usage, alerts |
| `realtime` | WebSocket/SSE broadcast layer |
| `dashboard` | Frontend UI, subscribes to realtime + calls REST for initial load |
| `discord-bot` | Command handlers, calls backend REST API |
| `llm-formatter` (optional) | Converts raw data → friendly sentence for bot replies |

### 5.3 Suggested Folder Structure

```
office-monitor/
├── backend/
│   ├── src/
│   │   ├── models/          # Device, Room, Alert schemas
│   │   ├── simulator/        # tick loop, state generator
│   │   ├── services/
│   │   │   ├── alertEngine.js
│   │   │   └── usageCalculator.js
│   │   ├── routes/
│   │   │   ├── devices.js
│   │   │   ├── rooms.js
│   │   │   ├── usage.js
│   │   │   └── alerts.js
│   │   ├── realtime/          # socket.io or SSE handlers
│   │   ├── db/                # SQLite setup or in-memory store
│   │   └── index.js
│   ├── package.json
│   └── .env.example
├── dashboard/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DeviceStatusPanel.jsx
│   │   │   ├── PowerMeter.jsx
│   │   │   ├── AlertsPanel.jsx
│   │   │   └── OfficeLayout.jsx   # bonus visual
│   │   ├── hooks/useLiveData.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── discord-bot/
│   ├── src/
│   │   ├── commands/
│   │   │   ├── status.js
│   │   │   ├── room.js
│   │   │   └── usage.js
│   │   ├── services/apiClient.js
│   │   ├── services/llmFormatter.js   # optional
│   │   └── index.js
│   └── package.json
├── diagrams/
│   ├── system-diagram.png
│   └── circuit-schematic-link.md      # link/screenshot from Wokwi/Tinkercad
├── docs/
│   └── ARCHITECTURE.md
└── README.md
```

### 5.4 Database Schema (SQLite recommended for simplicity)

**`rooms`**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT | "Drawing Room", "Work Room 1", "Work Room 2" |

**`devices`**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT | "Fan 1", "Light 2", etc. |
| type | TEXT | "fan" \| "light" |
| room_id | INTEGER FK → rooms.id | |
| status | BOOLEAN | on/off |
| power_watts | INTEGER | wattage when on (fan ~60W, light ~15W) |
| last_changed | DATETIME | updates on every status flip |
| on_since | DATETIME (nullable) | set when turned on, cleared when turned off — needed for the ">2hr continuous" alert rule |

**`alerts`**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| type | TEXT | "after_hours" \| "prolonged_room_on" |
| room_id | INTEGER FK (nullable) | |
| device_id | INTEGER FK (nullable) | |
| message | TEXT | human-readable |
| created_at | DATETIME | |
| resolved_at | DATETIME (nullable) | |

**`usage_log`** (for kWh estimation)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| timestamp | DATETIME | snapshot time |
| total_watts | INTEGER | total draw at that moment |

> `kWh estimate` = integrate `total_watts` over time (trapezoid or simple average × hours elapsed since 9 AM).

### 5.5 API List

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/devices` | All 15 devices with current state |
| GET | `/api/devices/:id` | Single device detail |
| GET | `/api/rooms` | All rooms with nested devices |
| GET | `/api/rooms/:name` | One room's devices + room-level wattage |
| GET | `/api/usage/current` | Total watts right now + per-room breakdown |
| GET | `/api/usage/today` | Estimated kWh so far today |
| GET | `/api/alerts` | Active (and optionally resolved) alerts |
| WS/SSE | `/realtime` | Push channel: `device-update`, `alert-created` events |
| (Optional) POST | `/api/devices/:id/toggle` | Manual override — useful for demo control, not required |

### 5.6 Required Integrations

- **Discord Developer Portal** — bot application + token, invited to a test server with `bot` + `applications.commands` scopes (or classic prefix commands, e.g. `!status`, which only needs message content intent).
- **Wokwi or Tinkercad** — free account for the schematic; Wokwi is generally better for ESP32 + code-based simulation, Tinkercad is more drag-and-drop friendly for beginners.
- **(Optional) LLM API** — Claude or OpenAI API key for humanizing bot responses; **must have a non-LLM fallback** so the bot still works if the API key/quota fails during a live demo.

### 5.7 Technology Stack (beginner-friendly)

| Layer | Recommended | Why | Alternative |
|---|---|---|---|
| Backend | Node.js + Express | Same language as bot + easy WebSocket support via `socket.io` | Python + FastAPI |
| Real-time | `socket.io` | Handles reconnects, fallbacks automatically | raw WebSocket, or SSE (simpler, one-directional — sufficient here) |
| Database | SQLite (`better-sqlite3`) | Zero setup, file-based, plenty for 15 devices | In-memory JS object + JSON file backup |
| Dashboard | React (Vite) + Tailwind CSS | Component reuse for 15 repeated device cards | Plain HTML/CSS/JS if team is less experienced |
| Discord bot | `discord.js` v14 | Best-documented, huge community | `discord.py` if team prefers Python |
| LLM (optional) | Claude API (Haiku-tier model for cost/speed) | Fast, cheap, good at short friendly replies | OpenAI GPT-4o-mini |
| Hosting (demo) | Render/Railway (backend), Vercel (dashboard) | Free tiers, quick deploy | Run everything locally for the video demo — perfectly acceptable |
| Circuit design | Wokwi | Code-first, ESP32-friendly, easy to share a link | Tinkercad |

---

## 6. Development Roadmap (Phase 0 → Final Output)

| Phase | Objectives | Key Tasks | Deliverables | Difficulty | Prerequisites |
|---|---|---|---|---|---|
| **0 – Requirement Analysis** | Fully understand the brief, resolve ambiguities (e.g., 15 vs 18 devices) | Re-read PDF; list every explicit + implied requirement; write down assumptions | This blueprint / a shared requirements doc | ⭐ Easy | None |
| **1 – Planning** | Lock architecture & task split | Choose stack; assign backend/dashboard/bot/diagrams to team members; set up repo, `.gitignore`, branch strategy | GitHub repo skeleton, task board (Trello/GitHub Projects) | ⭐ Easy | Phase 0 |
| **2 – UI/UX** | Design dashboard layout before coding it | Sketch wireframe (paper or Figma) for: status panel, power meter, alerts panel, optional office layout | Wireframe image(s) | ⭐⭐ Medium | Phase 1 |
| **3 – Backend Core** | Stand up API skeleton + data model | Init Express/FastAPI project; define DB schema; scaffold routes (empty responses first) | Running backend with stub endpoints | ⭐⭐ Medium | Phase 1 |
| **4 – Database & Simulator** | Real device data that changes over time | Implement DB tables; write simulator tick loop (randomly toggle devices, update `last_changed`/`on_since`) | Simulator producing believable live data in DB | ⭐⭐⭐ Medium-High | Phase 3 |
| **5 – APIs** | Expose full data + aggregation logic | Implement all endpoints in §5.5; implement usage/kWh calculator; implement alert rule engine | Fully functional REST API, testable via Postman/curl | ⭐⭐⭐ Medium-High | Phase 4 |
| **6 – AI/ML (optional)** | Humanize bot responses | Integrate LLM call in bot's response formatter with a static-template fallback | `llmFormatter.js` module with fallback tested | ⭐⭐ Medium | Phase 5 |
| **7 – Integration** | Connect dashboard + bot to backend | Add WebSocket/SSE broadcast on state/alert change; build dashboard components consuming live channel; build bot commands calling REST API | Working end-to-end system (dashboard + bot both reflect same live data) | ⭐⭐⭐⭐ High | Phases 5–6 |
| **8 – Testing** | Verify correctness & resilience | Test alert rules with edge cases (all devices off, all on, exactly 2hr boundary); test bot commands with malformed room names; test dashboard reconnect after backend restart | Test notes / checklist in repo | ⭐⭐⭐ Medium-High | Phase 7 |
| **9 – Deployment** | Make it demoable without "works on my machine" risk | Deploy backend + dashboard (or prepare rock-solid local run instructions); set final `.env.example`; write README | Deployed URLs or verified local setup, final README | ⭐⭐ Medium | Phase 8 |
| **10 – Demo Preparation** | Nail the 3-minute video | Script the walkthrough (architecture → dashboard live → bot commands → alert trigger); record; trim | Video demo file/link, diagrams finalized in `diagrams/` | ⭐⭐ Medium | Phase 9 |

---

## 7. Beginner's Guide (First Hackathon)

### What to build first
1. **Data model + simulator** (Phase 4) — everything else depends on this being real and dynamic. A convincing fake "live office" is the foundation of the whole project.
2. **Backend REST API** — get `/api/devices` returning real data before touching any frontend.
3. **Dashboard status panel** — the single most heavily-weighted item (20%). Get it live-updating before adding visuals/animation.
4. **Discord bot's `!status` command** — simplest command, proves the shared-backend architecture works end-to-end.

### What to ignore initially
- The animated top-view office layout (bonus points) — build it **last**, only if time remains.
- LLM-based response humanizing — get the bot working with plain template strings first, add the LLM layer as a polish pass.
- Deployment/hosting — build and demo locally first; only deploy if you have spare time and want a live link in the README.
- The "manual toggle" control endpoint — not required, easy to scope-creep into.

### Common mistakes to avoid
- **Two separate fake datasets** for dashboard and bot (violates the "single source of truth" requirement — this is explicitly graded).
- **Static demo data that never changes** — judges will notice a dashboard that looks the same the whole demo.
- **Polling everywhere instead of push updates** — the brief explicitly says "without requiring a page refresh"; aggressive client-side polling can technically satisfy this but a WebSocket/SSE push is cleaner and scores better on "quality of demo."
- **Wiring all 18 (or 15) devices in the schematic** — the brief explicitly says one representative room is enough; don't waste time over-engineering it.
- **Using Mermaid for the system diagram** — explicitly disallowed; use draw.io, Excalidraw, Figma, or a hand-drawn photo.
- **Forgetting the `on_since` field** — without it you cannot correctly implement the ">2 hours continuously on" alert.
- **Committing secrets** (Discord token, LLM API key) to the repo.

### Recommended Git workflow
- `main` branch always demo-able.
- Feature branches: `feature/backend-api`, `feature/dashboard-ui`, `feature/discord-bot`, `feature/simulator`.
- Small, frequent commits with clear messages (e.g., `feat: add alert rule engine for after-hours devices`) — commit quality is explicitly graded (15%).
- Open PRs even in a small team; merge to `main` only when a piece works end-to-end — avoids a broken `main` right before the demo.

### Team task distribution (suggested for a 3–4 person team)
| Role | Owns |
|---|---|
| Backend/DB lead | Data model, simulator, alert engine, REST API |
| Frontend lead | Dashboard UI, live status/power/alerts panels, optional office layout visual |
| Bot/Integration lead | Discord bot commands, LLM formatter, connecting bot to backend |
| Docs/Diagrams lead (can be shared) | System diagram, circuit schematic, README, demo video script/editing |

### Daily progress plan (assuming a 2–3 day hackathon)

| Day | Focus |
|---|---|
| Day 1 AM | Phases 0–2: finalize requirements, architecture, wireframes, repo setup |
| Day 1 PM | Phases 3–4: backend skeleton + simulator producing live changing data |
| Day 2 AM | Phase 5: full API + alert engine + usage calculator |
| Day 2 PM | Phase 7 (start): dashboard live panel wired to backend; bot `!status`/`!room`/`!usage` wired |
| Day 3 AM | Phase 6 (LLM polish) + bonus features if time allows (office layout visuals, proactive bot alerts) |
| Day 3 PM | Phases 8–10: testing, README, diagrams finalized, record demo video |

---

## 8. MVP (Minimum to Submit a Working Project)

To satisfy every explicitly-graded criterion at a baseline level:

- [ ] Simulated data for 15 devices (status, wattage, room, `last_changed`) that changes over time
- [ ] Backend API as single source of truth (REST, at minimum `/api/devices`, `/api/rooms/:name`, `/api/usage/current`)
- [ ] Dashboard: live device status panel grouped by room, updates without refresh
- [ ] Dashboard: live total + per-room power meter
- [ ] Dashboard: alerts panel (after-hours + >2hr-continuous rules), timestamped
- [ ] Discord bot: `!status`, `!room <name>`, `!usage`, pulling real data from the backend
- [ ] System diagram (non-Mermaid) showing device → simulator → backend → dashboard + bot → user
- [ ] Circuit schematic (Wokwi or Tinkercad) for one representative room
- [ ] Public repo with README covering setup for backend, dashboard, and bot
- [ ] Video demo (≤3 min)

This alone covers 100% of the explicit weighted criteria — bonus items below are purely score-boosting.

---

## 9. Extra Features (Realistic Hackathon-Winning Additions)

Ranked by effort-to-impact ratio:

1. **Top-view office layout with live visual state** (explicitly called out as bonus) — glowing lights, spinning fan icons. High visual impact for a demo video, moderate effort if using simple CSS animations on an SVG floor plan.
2. **Proactive Discord alerts** (explicitly called out as bonus) — bot posts to a channel when an alert fires. Low effort once the alert engine exists — just add a webhook/send-message call.
3. **Historical usage chart** (line chart of wattage over the last hour) — moderate effort, strong "polish" signal, and reuses your `usage_log` table.
4. **Dark/light theme toggle or a clean design system** — low effort, improves "Dashboard visuals and UX quality" score (10%).
5. **Manual device control from the dashboard** (toggle a device, see it reflected instantly in Discord too) — nice "wow" moment in a demo, moderate effort, not required.
6. **Current-sensing concept in schematic** (e.g., an ACS712 sensor symbol feeding an ESP32 ADC pin) — low effort (it's just a diagram addition), directly addresses the brief's "optionally sensing current draw."

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **15 vs 18 device count discrepancy** in the brief | Data model built on wrong assumption | Confirm with organizers early; document your chosen interpretation (15: 6 fans + 9 lights) explicitly in the README so judges see it was a deliberate, reasoned choice, not an oversight |
| Simulator produces unrealistic/static-feeling data | Dashboard looks fake in the demo, hurts "quality of demo & dummy data simulation" (15%) | Vary tick timing slightly, ensure changes are visible during the exact demo window, test the live look before recording |
| Dashboard and bot briefly disagree due to caching | Violates "single source of truth" requirement | Always read from backend on each bot command (no bot-side caching); dashboard uses push updates, not local mutation |
| WebSocket/SSE complexity eats too much time for a beginner team | Core feature ("no refresh") missed or buggy | If time-pressured, simple **short-interval polling (e.g., every 3–5s)** is an acceptable fallback — still satisfies "no manual refresh," just less elegant |
| LLM API key issues during live demo (rate limit, network) | Bot appears broken on stage | Always implement a template-string fallback response; never let the bot fail silently if the LLM call errors |
| Team runs out of time before the schematic/diagram | Loses 30% combined (diagram + schematic) despite working software | Timebox diagram/schematic work explicitly in the Day 1 plan — don't leave them for the last hour |
| ">2 hours continuous" alert never triggers during a short demo | Alert panel looks empty/untested on camera | For the demo recording, either seed a device with a pre-set `on_since` far in the past, or temporarily lower the threshold (e.g., 2 minutes) for demo purposes and mention this in the video |
| Discord bot token / API keys accidentally committed | Security exposure, possible bot hijack | `.env` in `.gitignore` from the first commit; use `.env.example` with placeholder values in the repo |
| Mermaid used by mistake for the system diagram | Explicit requirement violated | Use Excalidraw, draw.io, or Figma — flag this early since it's an easy accidental miss |

---

*Prepared as a planning reference for the Techathon Nationals & Rover Summit preliminary round. Confirm the 15-vs-18 device discrepancy with organizers before finalizing the data model.*
