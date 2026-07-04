# Development Process — Phase by Phase (Updated)
**Project: Office IoT Monitoring System ("Lights, Fans, Discord")**
**Stack: Python Flask · MySQL · discord.py · React (Vite)**
**Based on: Hackathon Problem Statement (Preliminary Round) v1.2**

> This plan is cross-referenced directly against the official PDF problem statement.
> Each phase maps explicitly to graded criteria percentages.

---

## 📋 Grading Weights (from PDF — memorize these)

| Criterion | Weight |
|---|---|
| Working web dashboard with real-time data | **20%** |
| Dashboard visuals and UX quality | **10%** |
| Working Discord bot reflecting real simulated data | **10%** |
| Clear, correct system diagram | **15%** |
| Sensible circuit schematic | **15%** |
| Quality of demo & dummy data simulation | **15%** |
| Well structured and documented codebase, commits | **15%** |
| **Total** | **100%** |

> Diagrams + schematic = **30%** combined. Do NOT leave these for last.
> Dashboard (real-time behavior + visuals) = **30%** combined. Top priority in code.

---

## 🏢 Fixed Office Setup (from PDF)

| Room | Fans | Lights | Devices |
|---|---|---|---|
| Drawing Room | 2 | 3 | 5 |
| Work Room 1 | 2 | 3 | 5 |
| Work Room 2 | 2 | 3 | 5 |
| **Total** | **6** | **9** | **15** |

> **Device count decision: 15.** The PDF layout calculates to 15 (2 fans + 3 lights × 3 rooms = 15).
> Documented in docs/ASSUMPTIONS.md. Seed data uses 15.

---

## Phase 0 — Requirement Analysis ✅ (Complete)
**Owner:** Whole team

### What was resolved
- ✅ Device count ambiguity: **15 devices** chosen, documented in docs/ASSUMPTIONS.md
- ✅ Stack locked: Python Flask + MySQL + discord.py + React/Vite
- ✅ Grading weights studied and visible in this document
- ✅ Repo created with remote: https://github.com/jaherunhasanrimon/office-iot-monitoring-system.git
- ✅ Full folder structure scaffolded

### Remaining task
- [ ] Pin grading weight table to team's Discord or task board header

---

## Phase 1 — Planning ✅ (Largely Complete)
**Owner:** Team lead

### What was done
- ✅ GitHub repo initialized with remote
- ✅ Full folder structure created (backend/, dashboard/, discord-bot/, diagrams/, docs/)
- ✅ .gitignore configured (secrets, venv, node_modules)
- ✅ All .env.example files created for all 3 services
- ✅ README.md with 3 separate run sections (backend / dashboard / bot)

### Remaining tasks
- [ ] Set up a task board (GitHub Projects) with Backlog → In Progress → Review → Done
- [ ] Seed task board with tasks from Phases 2–12
- [ ] Agree on branch strategy: feature/backend-api, feature/dashboard-ui, feature/discord-bot, feature/simulator
- [ ] Each person do their first git commit (commit history graded at 15%)

### Exit Criteria
- [ ] main branch is protected/clean
- [ ] All 3 .env.example files verified present
- [ ] Every team member has committed at least once

---

## Phase 2 — UI/UX Design
**Estimated time:** 1–2 hours | **Owner:** Frontend lead (+ input from all)

### Steps
1. Sketch the dashboard in Figma/Excalidraw. Mandatory 3 zones:
   - Zone 1 — Device Status Panel: 15 cards grouped by 3 rooms. Each card: device name, icon (fan/light), ON/OFF state, wattage.
   - Zone 2 — Power Meter: Total office watts (large, prominent). Per-room breakdown. Today's estimated kWh.
   - Zone 3 — Active Alerts Panel: Timestamped, newest first. Two badge types: "After Hours" (red) and "Prolonged ON" (amber).
2. Decide visual language for device state:
   - Fan ON → spinning CSS animation. Fan OFF → static.
   - Light ON → amber/yellow glow. Light OFF → gray.
3. Design connection badge: "● Live" (green) vs "○ Disconnected" (red) in the header.
4. [Bonus] Top-view SVG floor plan of 3 rooms — device icons placed in correct positions. State reflected by CSS class toggling.
5. Team 5-minute gut-check on wireframe before coding starts.

### PDF-specific note
PDF calls out: "lights should glow when ON, and fans should animate when running."
"Dashboard visuals and UX quality" is 10% of grade — don't make it look like a plain data table.

### Exit Criteria
- [ ] Wireframe saved to diagrams/wireframe.png or Figma link in README
- [ ] Color/state legend agreed: status: true/false (not 1/0, not "on"/"off")

### Pitfalls
- Building bonus SVG layout before core 3-zone panel works.
- Generic Bootstrap-style look — visuals are explicitly graded.

---

## Phase 3 — Backend Core (Skeleton)
**Estimated time:** 2–3 hours | **Owner:** Backend lead

### Steps
1. Install dependencies in backend/ venv:
   ```
   cd backend && python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create MySQL database: CREATE DATABASE office_iot;
3. Copy .env.example → .env and fill in MySQL credentials.
4. Run python run.py — confirm GET /api/health returns {"status": "ok"}.
5. Verify GET /api/devices returns 15 seeded devices with correct room assignments and wattage (fan ~60W, light ~15W).
6. Check CORS allows dashboard on port 5173 to call backend on 5000.

### Code files already scaffolded (verify & complete if needed)
- backend/app/__init__.py — Flask app factory ✅
- backend/app/models.py — Room, Device, Alert, UsageLog models ✅
- backend/app/db.py — SQLAlchemy + seed script (3 rooms, 15 devices) ✅
- backend/app/routes/health.py ✅
- backend/app/routes/devices.py ✅
- backend/app/routes/rooms.py ✅
- backend/app/routes/usage.py ✅
- backend/app/routes/alerts.py ✅
- backend/run.py ✅

### Exit Criteria
- [ ] GET /api/health → 200
- [ ] GET /api/devices → 15 devices, each with id, name, type, room_id, room_name, status, power_watts, last_changed, on_since
- [ ] GET /api/rooms → 3 rooms, each with nested devices list and total_watts
- [ ] Backend starts with single command: python run.py

### Pitfalls
- Hardcoding room/device logic instead of driving it from DB.
- Not testing with curl/Postman at this stage.

---

## Phase 4 — Database & Simulator
**Estimated time:** 3–4 hours | **Owner:** Backend lead

### Steps
1. Verify APScheduler simulator in backend/app/simulator.py:
   - tick_devices(app) runs every SIMULATOR_TICK_SECONDS (default 15s).
   - On each tick: 1–3 random devices toggle. ON → on_since = now, OFF → on_since = None.
   - After tick: calls alert_engine.evaluate(), emits SocketIO events.
2. Verify log_usage(app) job runs every USAGE_LOG_INTERVAL_SECONDS (300s) and writes to usage_log table.
3. Test simulator standalone for 2+ minutes. Check MySQL directly:
   SELECT name, status, on_since, last_changed FROM devices;
   SELECT * FROM usage_log ORDER BY timestamp DESC LIMIT 10;
4. Verify usage_calculator.py:
   - get_current_watts() = SUM of power_watts WHERE status = TRUE
   - get_today_kwh() = trapezoidal integration of usage_log since 9 AM
5. Set SIMULATOR_TICK_SECONDS=15 for development. Tune to 5–8s before recording demo video.

### Exit Criteria
- [ ] Running backend 2+ minutes → at least 1 device changes state in MySQL
- [ ] on_since correctly sets on ON and clears (NULL) on OFF
- [ ] usage_log accumulates rows over time
- [ ] GET /api/usage/current returns correct live wattage
- [ ] GET /api/usage/today returns non-zero kWh after several log entries

### Pitfalls
- on_since not clearing on OFF — silently breaks Rule B (the > 2hr continuous alert). Most common bug.
- APScheduler use_reloader=False must be set in socketio.run() — otherwise scheduler starts twice in debug mode.

---

## Phase 5 — APIs & Alert Engine
**Estimated time:** 3–4 hours | **Owner:** Backend lead (+ 1 support)

### Steps
1. Verify all real endpoints in backend/app/routes/:

   Endpoint                  | Expected response
   GET /api/devices          | List of 15 devices with full state
   GET /api/devices/<id>     | Single device
   GET /api/rooms            | 3 rooms with nested devices + total_watts
   GET /api/rooms/<name>     | Case-insensitive match (e.g., work1 → Work Room 1)
   GET /api/usage/current    | { total_watts, per_room: [...] }
   GET /api/usage/today      | { estimated_kwh: float }
   GET /api/alerts           | Active unresolved alerts, newest first

2. Verify alert engine in backend/app/services/alert_engine.py:
   - Rule A (after-hours): Device ON when hour < 9 or hour >= 17
   - Rule B (prolonged room-on): ALL devices in a room have status=True AND all on_since older than 2 hours
   - Deduplication: Only INSERT new alert if no existing unresolved alert of same type + scope
   - Resolution: When condition clears → UPDATE alerts SET resolved_at = NOW()

3. Test alert rules manually via SQL:
   Force Rule B: UPDATE devices SET status=TRUE, on_since=DATE_SUB(NOW(), INTERVAL 3 HOUR) WHERE room_id=1;
   Confirm GET /api/alerts shows prolonged_room_on alert for Drawing Room.

4. Test Rule A by setting OFFICE_HOURS_START=0, OFFICE_HOURS_END=0 in .env.

5. Test GET /api/rooms/doesnotexist → must return 404 JSON, not crash.

### PDF alert requirement (p.3)
"devices left on after office hours (assume office hours are 9 AM–5 PM), or a room where all devices have been on for more than 2 hours continuously. Alerts should be timestamped."

### Exit Criteria
- [ ] All 7 endpoints return correct real data
- [ ] Rule B triggers correctly when on_since is > 2hrs in the past
- [ ] Rule A triggers correctly outside 9–17 window
- [ ] No duplicate alerts on repeated ticks
- [ ] Unknown room name → 404 with JSON error body (not 500)
- [ ] resolved_at gets set when the alert condition clears

### Pitfalls
- Re-creating a fresh alert every tick instead of deduplicating.
- Room name matching not case-insensitive.

---

## Phase 6 — AI/ML Layer (LLM Polish)
**Estimated time:** 1–2 hours | **Owner:** Bot/Integration lead

### Steps
1. discord-bot/bot/services/llm_formatter.py is already scaffolded with:
   - Template string fallback (always works, zero dependencies)
   - Anthropic Claude Haiku / OpenAI GPT-4o-mini wrapper
   - try/except so any LLM failure falls back silently
2. Test WITHOUT LLM_API_KEY in .env — bot must still produce readable responses.
3. Add real LLM_API_KEY and test — responses should sound natural and friendly, not robotic.
4. Keep prompts short: single sentence + raw data. Keep max_tokens ≤ 150.
5. Test all 3 formatter functions: format_status(), format_room(), format_usage().

### PDF quote
"Responses should be humanized and friendly — the boss hates robotic data dumps. Using an LLM to generate conversational responses is strongly encouraged."

### Exit Criteria
- [ ] Bot works correctly with LLM_API_KEY unset (template fallback fires)
- [ ] Bot produces natural sentence with LLM enabled
- [ ] LLM calls complete in < 3 seconds

### Pitfalls
- No fallback path — single API quota hit during live demo breaks the entire bot.
- Using expensive Claude Opus / GPT-4 — use Haiku or GPT-4o-mini for speed and cost.

---

## Phase 7 — Flask-SocketIO Real-Time Layer
**Estimated time:** 2–3 hours | **Owner:** Backend lead

### Steps
1. Verify backend/app/realtime.py — emit_device_update() and emit_alert_created() called from simulator.py after each tick.
2. Confirm event payload shape matches React useLiveData.js hook expectations:
   - device_update → { id, name, type, room_id, room_name, status, power_watts, last_changed, on_since }
   - alert_created → { id, type, room_id, device_id, message, created_at, is_active }
3. Test with two browser tabs open at the same time — both must receive the same events.

### Exit Criteria
- [ ] Backend emits device_update event within ~1s of simulator tick
- [ ] Both browser tabs update simultaneously
- [ ] Backend restart → socket reconnects automatically

### Pitfalls
- use_reloader=True in Flask debug mode starts APScheduler twice — keep use_reloader=False.
- CORS policy blocking SocketIO from port 5173 — ensure cors_allowed_origins="*".

---

## Phase 8 — Integration (Dashboard + Bot ↔ Backend)
**Estimated time:** 4–6 hours | **Owner:** Frontend lead + Bot lead in parallel

### Frontend integration steps
1. Install dashboard dependencies and start dev server:
   cd dashboard && npm install && npm run dev
2. Verify useLiveData.js hook:
   - Initial load fetches /api/devices, /api/usage/current, /api/usage/today, /api/alerts
   - SocketIO subscribes to device_update and alert_created events
   - State patches correctly without full re-render
3. Build DeviceStatusPanel:
   - Group devices by room_name
   - Fan card: spinning CSS animation when status=true
   - Light card: amber glow class when status=true, gray when false
   - Show power_watts only when ON
4. Build PowerMeter:
   - Total watts prominently displayed (large number)
   - Per-room row for each of 3 rooms
   - Today's estimated kWh
5. Build AlertsPanel:
   - Filter is_active=true alerts only
   - Sort newest first (created_at DESC)
   - Badge: "After Hours" (red) | "Prolonged ON" (amber)
6. Add connection indicator in header: "● Live" (green) | "○ Disconnected" (red/gray)
7. [BONUS] OfficeLayout.jsx — SVG top-view with device icons in correct rooms, CSS toggled by status

### Bot integration steps
1. Copy .env.example → .env in discord-bot/, fill in DISCORD_TOKEN and BACKEND_URL.
2. Install bot dependencies and run:
   cd discord-bot && python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt && python run.py
3. Test all commands in your Discord server:
   !status → summary of all 3 rooms
   !room drawing → Drawing Room status
   !room work1 → Work Room 1 status
   !room work2 → Work Room 2 status
   !usage → total watts + today's kWh
4. [BONUS] Proactive alert posting — poll /api/alerts every 30s, diff against known alert IDs, post new ones to configured channel.
5. Test bot edge cases:
   - !room doesnotexist → friendly error message, not a crash
   - !room (empty arg) → usage hint
   - !room Work1 (capitalized) → should work (case-insensitive on backend)

### PDF requirement
"The web dashboard and the Discord bot must share a single backend. There should be one source of truth for device state — both interfaces read from it."

### Exit Criteria
- [ ] Toggling a device via simulator appears on dashboard within ~1–2 seconds, no page refresh
- [ ] !status, !room work1, !usage return real data matching dashboard at the same moment
- [ ] Dashboard shows "● Live" when connected and "○ Disconnected" when backend is stopped
- [ ] [Bonus] New alert → unprompted bot message in Discord channel

### Pitfalls
- Dashboard and bot reading from different code paths — always route both through same Flask API/MySQL.
- Not testing two browser tabs simultaneously.

---

## Phase 9 — Testing
**Estimated time:** 2–3 hours | **Owner:** Whole team (pair testing)

### Alert boundary tests
1. Force on_since to exactly 1h59m ago for all devices in a room → Rule B must NOT trigger.
2. Force on_since to 2h01m ago → Rule B MUST trigger.
   UPDATE devices SET status=TRUE, on_since=DATE_SUB(NOW(), INTERVAL 121 MINUTE) WHERE room_id=1;
3. Set OFFICE_HOURS_START=0, OFFICE_HOURS_END=0 → Rule A must trigger for all ON devices.
4. Set back to 9/17 → Rule A must NOT trigger (during 9–5).

### Bot edge case tests
- !room doesnotexist → friendly 404 message
- !room (empty) → usage hint
- !room Work1 (capitalized) → should work
- !usage when no usage_log rows → should return 0 kWh, not crash

### Dashboard tests
5. Restart backend while dashboard is open → connection badge goes red → reconnects within ~10s.
6. Open 2 browser tabs → both update simultaneously on same simulator tick.
7. Verify dashboard numbers and !usage bot output match at the same second.
8. Cross-browser: test in browser you will record the demo in.

### Exit Criteria
- [ ] All edge cases produce sensible behavior (no crashes, no silent failures)
- [ ] Written test checklist committed to docs/ or README.md test section

### Pitfalls
- Only testing the happy path — judges try !room doesnotexist out of curiosity.

---

## Phase 10 — Diagrams (Non-Code Deliverables — 30% of grade)
**Estimated time:** 2–3 hours | **Owner:** Docs/Diagrams lead

> IMPORTANT: This phase is worth 30% of the total grade combined. Do NOT leave it to the last 30 minutes.

### System Diagram (15%)
1. Create in Excalidraw, draw.io, or Figma. NOT Mermaid — explicitly disallowed in PDF.
2. Must show data flow:
   [APScheduler Simulator] → [MySQL DB] → [Alert Engine]
                                    ↓
                             [Flask REST API + Flask-SocketIO]
                               /              \
                    [Discord Bot]          [React Dashboard]
                    (REST, on demand)      (WebSocket, live push)
                         ↓                       ↓
                  [Discord Server]         [Boss's Browser]
3. Export as diagrams/system-diagram.png and reference from README.md.

### Circuit Schematic (15%)
1. Use Wokwi (preferred for ESP32) or Tinkercad.
2. Wire one representative room only (Drawing Room: 2 fans + 3 lights) — PDF explicitly says "one room is enough."
3. Minimum components:
   - ESP32 microcontroller
   - Relay module (one per device) for each fan/light
   - LED(s) representing lights
   - DC motor or fan symbol for fans
   - [Optional] ACS712 current sensor — addresses "optionally sensing current draw" in PDF
4. Export screenshot to diagrams/circuit-schematic.png AND paste share link in diagrams/circuit-schematic-link.md.

### Exit Criteria
- [ ] diagrams/system-diagram.png committed (non-Mermaid tool used)
- [ ] diagrams/circuit-schematic.png or Wokwi/Tinkercad link committed
- [ ] Both referenced from README.md

### Pitfalls
- Using Mermaid — PDF explicitly says "Do not use Mermaid for your diagrams."
- Wiring all 15 devices — waste of time, PDF says one room is enough.

---

## Phase 11 — Deployment & Final Run Setup
**Estimated time:** 1–2 hours | **Owner:** Backend lead + Docs lead

### Steps
1. Deployment decision: Local demo (simplest, zero infra risk) OR hosted:
   - Backend: Render/Railway (free tier — note cold start delay)
   - Dashboard: Vercel (free)
   - Bot: Keep running locally (always)
2. Finalize all .env.example files — every variable has a comment explaining it.
3. Clean-machine test: team member who didn't write backend follows README from scratch, fix gaps found.
4. Verify all 3 services start from documented commands:
   cd backend && python run.py
   cd dashboard && npm run dev
   cd discord-bot && python run.py
5. Final check: docs/ASSUMPTIONS.md has 15-vs-18 decision documented.
6. All diagrams committed to diagrams/ and linked from README.md.

### Exit Criteria
- [ ] README verified by someone other than the author
- [ ] All 3 services start clean from README alone
- [ ] diagrams/system-diagram.png in repo
- [ ] diagrams/circuit-schematic.png or link in repo

### Pitfalls
- README only tested by its author — #1 cause of judge setup failures.

---

## Phase 12 — Demo Preparation
**Estimated time:** 1–2 hours | **Owner:** Whole team

### Video script (3-minute strict budget)
0:00–0:30 | Problem + architecture — show diagrams/system-diagram.png, explain Flask/MySQL/React/discord.py stack
0:30–1:30 | Live dashboard — device panel updating live, power meter changing, point to active alert
1:30–2:30 | Discord bot — run !status, !room drawing, !usage live; show proactive alert if built
2:30–3:00 | Quick mention of circuit schematic + wrap-up

### Before recording
1. Force at least one alert condition so Alerts Panel isn't empty on camera:
   UPDATE devices SET status=TRUE WHERE id IN (1,2,3);
   Set OFFICE_HOURS_END=0 temporarily in .env so current time is "after hours"
2. Confirm simulator tick is ≤ 15s so changes are visible on camera.
3. Do one full dry run without recording — check timing and bot response quality.
4. Remove debug print() statements that would clutter terminal shown on screen.

### Exit Criteria
- [ ] Video ≤ 3 minutes
- [ ] Dashboard visibly updates live (no refresh) on camera
- [ ] Bot responds to at least !status and !usage on camera
- [ ] At least one alert visible in Alerts Panel
- [ ] Final repo push: all diagrams + README + docs committed

### Pitfalls
- Recording before forcing a demo-friendly alert condition — empty Alerts Panel undersells the feature.
- Terminal showing noisy debug output during recording.

---

## ⚡ Quick Reference: Phase → Grading Weight

| Phase | Builds toward | Weight |
|---|---|---|
| 3, 4, 5 | Quality of demo & dummy data simulation | 15% |
| 8 (frontend) | Working web dashboard with real-time data | 20% |
| 2, 8 (frontend visuals) | Dashboard visuals and UX quality | 10% |
| 6, 8 (bot) | Working Discord bot reflecting real simulated data | 10% |
| 10 (system diagram) | Clear, correct system diagram | 15% |
| 10 (schematic) | Sensible circuit schematic | 15% |
| 1, 9, 11 | Well structured and documented codebase, commits | 15% |

Use this table to sanity-check time allocation if running behind — don't let any 15%+ category go untouched.

---

## 🔴 Critical Risks & Mitigations

Risk | Impact | Mitigation
on_since not clearing on OFF | Rule B never works | Test in Phase 4 with direct DB query
Duplicate alert spam per tick | Alerts Panel floods | Deduplication check in alert_engine.py — test it
Dashboard and bot disagree | Violates "single source of truth" | Both always call same Flask API — never cache separately
LLM API fails during live demo | Bot appears broken | Template fallback coded in llm_formatter.py — test with key removed
System diagram in Mermaid | Explicit requirement violation | Use Excalidraw or draw.io
Empty Alerts Panel in demo video | Alert feature looks unbuilt | Force alert condition before recording (Phase 12)
Commit history is sparse | Loses 15% on codebase quality | Commit at end of each phase, use meaningful messages
