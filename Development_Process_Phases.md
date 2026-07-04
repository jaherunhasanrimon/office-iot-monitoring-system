# Development Process — Phase by Phase
**Project: Office IoT Monitoring System ("Lights, Fans, Discord")**

This expands the roadmap from the blueprint into an actionable, step-by-step process. Each phase includes: objective, detailed steps, technical notes, exit criteria (Definition of Done), estimated time, and phase-specific pitfalls.

Assumes a 3-day hackathon window and a 3–4 person team; adjust timing if your window differs.

---

## Phase 0 — Requirement Analysis
**Estimated time:** 1–2 hours | **Owner:** Whole team

### Steps
1. Read the problem statement together, line by line — don't split this up, everyone should hear it once as a group.
2. List every explicit requirement (use the Feature Analysis table from the blueprint as a starting checklist).
3. Flag ambiguities as a team — specifically the 15-vs-18 device count — and decide your team's official interpretation.
4. Write down assumptions in a shared doc (`docs/ASSUMPTIONS.md`) so judges see reasoning, not guesswork.
5. Identify what's explicitly graded vs. implied — rank effort accordingly (dashboard real-time + bot = 30%, diagrams = 30%, demo/data quality = 15%, code quality = 15%).

### Exit Criteria (Definition of Done)
- [ ] Every team member can state the 3 rooms, device counts, and required deliverables from memory
- [ ] `docs/ASSUMPTIONS.md` exists with the device-count decision and any other resolved ambiguities
- [ ] Grading weights are visible somewhere the team will actually see during the sprint (pinned message, task board header)

### Pitfalls
- Skipping this and jumping straight to code — the device-count ambiguity alone can silently break your alert logic later if not caught now.

---

## Phase 1 — Planning
**Estimated time:** 1–2 hours | **Owner:** Team lead + all

### Steps
1. Confirm tech stack (Node.js/Express + React + discord.js + SQLite, or your team's variant).
2. Create the GitHub repo with the folder structure from the blueprint (§5.3) — empty folders with `.gitkeep` are fine at this stage.
3. Set up `.gitignore` (node_modules, `.env`, build artifacts) **before the first commit with any secrets**.
4. Create `.env.example` files in `backend/` and `discord-bot/` listing required variables (`PORT`, `DISCORD_TOKEN`, `LLM_API_KEY`, etc.) with placeholder values.
5. Assign roles per the blueprint's team distribution (Backend/DB, Frontend, Bot/Integration, Docs/Diagrams).
6. Set up a task board (GitHub Projects/Trello) with columns: Backlog → In Progress → Review → Done. Seed it with tasks from Phases 3–10.
7. Agree on branch naming (`feature/xxx`) and a lightweight PR review rule (at least a self-review checklist if no time for peer review).

### Exit Criteria
- [ ] Repo exists, structure matches blueprint, `main` branch is protected/clean
- [ ] `.env.example` files committed, real `.env` gitignored
- [ ] Task board populated and assigned
- [ ] Everyone knows what they're building for the next 6 hours

### Pitfalls
- Choosing a stack nobody on the team actually knows well — pick tools for what your team can execute in 3 days, not what's "coolest."

---

## Phase 2 — UI/UX Design
**Estimated time:** 1–2 hours | **Owner:** Frontend lead (+ input from all)

### Steps
1. Sketch the dashboard layout on paper or in Figma/Excalidraw — three zones minimum: **Device Status**, **Power Meter**, **Alerts**.
2. Decide the visual language for device state: color (e.g., amber glow = on, gray = off), icon/animation for fans vs. lights.
3. If attempting the bonus office-layout visual, sketch the top-view SVG zones now (using the office layout image from the brief as reference) — decide whether it's SVG-based or a CSS grid of room "cards."
4. Design the alert card format: icon + message + timestamp + severity color.
5. Decide responsive behavior — will this be demoed on a laptop screen only, or does it need to work on a phone during the video?
6. Get a 5-minute team review/gut-check on the wireframe before coding starts.

### Exit Criteria
- [ ] Wireframe image saved to `diagrams/wireframe.png` (or Figma link in README)
- [ ] Color/state legend decided and written down (so backend field names match frontend expectations, e.g., `status: "on" | "off"` not `1/0` vs `true/false` mismatches)

### Pitfalls
- Designing the full animated office-layout bonus feature before the core 3-zone panel exists — sequence matters, bonus comes last.

---

## Phase 3 — Backend Core (Skeleton)
**Estimated time:** 2–3 hours | **Owner:** Backend lead

### Steps
1. Initialize backend project (`npm init`, install Express, `better-sqlite3` or chosen DB driver, `socket.io` or SSE dependencies).
2. Set up basic server (`index.js`) with a health-check route (`GET /api/health`).
3. Define the data models from the blueprint schema (§5.4): `rooms`, `devices`, `alerts`, `usage_log`.
4. Write a DB init/seed script that creates the 3 rooms and 15 devices (2 fans + 3 lights × 3 rooms) with initial `status`, `power_watts`, `last_changed`.
5. Scaffold route files (`routes/devices.js`, `routes/rooms.js`, `routes/usage.js`, `routes/alerts.js`) — return stub/hardcoded JSON initially just to unblock frontend/bot devs.
6. Set up CORS so the dashboard (different port) can call the API locally.

### Exit Criteria
- [ ] `GET /api/health` returns 200
- [ ] `GET /api/devices` returns 15 seeded devices with correct room assignment and wattage (fans ~60W, lights ~15W)
- [ ] Backend runs with a single documented command (`npm run dev`)

### Pitfalls
- Hardcoding room/device logic instead of driving it from the DB — makes later changes (e.g., resolving the 15-vs-18 question) painful.

---

## Phase 4 — Database & Simulator
**Estimated time:** 3–4 hours | **Owner:** Backend lead

### Steps
1. Implement the simulator as an interval loop (e.g., `setInterval`, every 10–30s):
   - Randomly select a small number of devices to toggle.
   - On toggle to **ON**: set `status = true`, `last_changed = now`, `on_since = now`.
   - On toggle to **OFF**: set `status = false`, `last_changed = now`, `on_since = null`.
2. Add a separate interval (e.g., every 5 min, or shortened for demo purposes) that writes a row to `usage_log` with the current total wattage — this feeds the "today's estimated kWh" calculation.
3. Write the usage calculator: sum `power_watts` of all `status=true` devices for "current," and integrate `usage_log` rows since 9 AM for "today's estimate."
4. Test the simulator standalone (log to console) before wiring it to the API, to confirm state actually mutates over multiple ticks.
5. Decide and document the tick interval — note it explicitly in the README since judges may ask "how often does this update?"

### Exit Criteria
- [ ] Running the backend for 2+ minutes shows at least one device changing state in the DB
- [ ] `on_since` correctly clears on OFF and sets on ON
- [ ] `usage_log` accumulates rows over time

### Pitfalls
- Forgetting to clear `on_since` on OFF — this silently breaks the "room on >2hrs continuously" alert rule later.
- Simulator interval too slow to show visible change during the 3-minute demo recording — tune this deliberately before recording, not after.

---

## Phase 5 — APIs & Alert Engine
**Estimated time:** 3–4 hours | **Owner:** Backend lead (+ 1 support)

### Steps
1. Implement all real endpoints from blueprint §5.5, backed by the DB (replace Phase 3 stubs):
   - `GET /api/devices`, `GET /api/devices/:id`
   - `GET /api/rooms`, `GET /api/rooms/:name`
   - `GET /api/usage/current`, `GET /api/usage/today`
   - `GET /api/alerts`
2. Implement the alert rule engine, run on each simulator tick:
   - **Rule A (after-hours):** any device with `status=true` where current time is outside 9 AM–5 PM → create/update an `after_hours` alert.
   - **Rule B (prolonged room-on):** for each room, if *all* devices in that room have `status=true` AND `on_since` for each is older than 2 hours → create a `prolonged_room_on` alert.
3. Avoid duplicate alert spam: check if an unresolved alert of the same type/room/device already exists before creating a new one; mark `resolved_at` when the condition clears.
4. Add basic input validation (e.g., `!room <name>` should 404 gracefully for an unknown room, not crash).
5. Manually test every endpoint with curl/Postman using real seeded data.

### Exit Criteria
- [ ] All endpoints from §5.5 return correct, real data
- [ ] Forcing a device `on_since` value 2+ hours in the past (via test script or DB edit) correctly triggers Rule B
- [ ] Setting system/test time outside 9–5 (or testing with a mocked clock) correctly triggers Rule A
- [ ] No duplicate alert spam on repeated ticks

### Pitfalls
- Re-creating a fresh alert every single tick instead of checking for an existing unresolved one — floods the Alerts Panel with duplicates.

---

## Phase 6 — AI/ML Layer (Optional Polish)
**Estimated time:** 1–2 hours | **Owner:** Bot/Integration lead

### Steps
1. Write the **template fallback first** — plain string formatting for `!status`, `!room`, `!usage` (e.g., `"${room}: ${fansOn} fan(s) ON, ${lightsOn} light(s) ON."`). This must work with zero external dependencies.
2. Add an `llmFormatter.js` that takes the raw JSON response and asks the LLM to phrase it conversationally (short prompt, low max tokens — this is a one-liner reply, not an essay).
3. Wrap the LLM call in a try/catch — on any failure (timeout, rate limit, missing key), fall back to the template string silently (log the error, don't show it to the user).
4. Test with the API key removed entirely to confirm the fallback path works — this is your insurance against a live-demo failure.

### Exit Criteria
- [ ] Bot works correctly with `LLM_API_KEY` unset (falls back cleanly)
- [ ] Bot produces a noticeably more natural sentence with the LLM enabled
- [ ] LLM calls are short/cheap (single short prompt, small max_tokens) to avoid latency during the demo

### Pitfalls
- No fallback path — a single API hiccup during the live demo takes the whole bot down.

---

## Phase 7 — Integration (Dashboard + Bot ↔ Backend)
**Estimated time:** 4–6 hours | **Owner:** Frontend lead + Bot lead in parallel

### Frontend integration steps
1. On dashboard load, call REST endpoints once for initial state (`/api/devices`, `/api/usage/current`, `/api/alerts`).
2. Open a WebSocket (`socket.io-client`) or SSE (`EventSource`) connection; on `device-update` / `alert-created` events, patch local state and re-render — no polling, no manual refresh.
3. Build `DeviceStatusPanel` (grouped by room, 15 cards/rows), `PowerMeter` (total + 3 room breakdowns), `AlertsPanel` (timestamped list, newest first).
4. If attempting the bonus office layout: bind device state to the SVG/CSS elements (glow class toggled by `status`).

### Backend integration steps
1. On every simulator tick / alert evaluation, emit `device-update` and `alert-created` events over the socket/SSE channel to all connected dashboard clients.
2. Confirm payload shape matches what the frontend expects (agree on this JSON contract in Phase 2/3, don't leave it implicit).

### Bot integration steps
1. Implement `!status`, `!room <name>`, `!usage` command handlers, each calling the relevant REST endpoint via `apiClient.js`.
2. Route the raw response through `llmFormatter.js` (Phase 6) before replying.
3. (Bonus) Add a listener/webhook so that when the backend detects a new alert, the bot posts to a configured Discord channel — either via a backend webhook call to Discord, or by having the bot itself poll `/api/alerts` on a short interval and diff against what it's already posted.

### Exit Criteria
- [ ] Toggling a device (via simulator or manual DB edit) appears on the dashboard within a few seconds, with **no page refresh**
- [ ] `!status`, `!room work1`, `!usage` all return real, current data matching the dashboard exactly at that moment
- [ ] (Bonus) A forced alert condition results in an unprompted bot message in the designated channel

### Pitfalls
- Dashboard and bot reading from two different code paths that could drift — always route both through the same backend API/DB, never a second in-memory copy.
- Forgetting to test on a **second/incognito browser tab** to confirm multiple dashboard clients get the same live updates.

---

## Phase 8 — Testing
**Estimated time:** 2–3 hours | **Owner:** Whole team (pair testing)

### Steps
1. **Alert boundary testing:** force a device to exactly 1h59m and 2h01m "on" duration and confirm the >2hr rule fires only in the second case.
2. **After-hours testing:** mock/adjust system time (or add a debug override) to confirm devices ON outside 9–5 correctly trigger Rule A, and correctly *don't* trigger during 9–5.
3. **Bot edge cases:** `!room doesnotexist`, `!room ` (empty), casing differences (`!room Work1` vs `!room work1`).
4. **Reconnection test:** restart the backend while the dashboard is open — confirm the dashboard either reconnects the socket or clearly indicates a disconnected state (don't leave it silently frozen with stale data).
5. **Consistency test:** compare dashboard numbers and `!usage` bot output side-by-side at the same moment — they must match.
6. **Cross-browser/device check** if presenting live, otherwise at least test in the browser you'll record with.

### Exit Criteria
- [ ] All edge cases above produce sensible behavior (no crashes, no silent failures)
- [ ] A written test log/checklist exists in the repo (even a simple markdown checklist counts toward "well structured and documented")

### Pitfalls
- Only testing the happy path — judges (or a live demo audience) will often try an edge case out of curiosity (e.g., typing a nonsense room name).

---

## Phase 9 — Deployment / Final Run Setup
**Estimated time:** 1–2 hours | **Owner:** Backend lead + Docs lead

### Steps
1. Decide: deploy live (Render/Railway for backend, Vercel for dashboard) or run locally for the demo — either is acceptable, but **local must be flawless** if chosen.
2. Finalize `.env.example` for all three services with every required variable documented.
3. Write the README: prerequisites, install steps, run commands for **backend**, **dashboard**, and **bot** as three clearly separate sections, plus how to invite/test the Discord bot.
4. Do a **clean-machine test**: have a team member who didn't write the backend try to set it up from the README alone, timing how long it takes and noting any missing steps.
5. Finalize and copy diagrams (`system-diagram.png`, schematic screenshot/link) into `diagrams/` and reference them from the README.

### Exit Criteria
- [ ] README setup instructions verified by someone other than the original author
- [ ] All three services start successfully from documented commands alone
- [ ] Diagrams present in the repo, not just pasted in a chat/Docs link that could go stale

### Pitfalls
- README written by the person who built it, never tested by anyone else — the #1 cause of "we couldn't run the judge's copy" complaints.

---

## Phase 10 — Demo Preparation
**Estimated time:** 1–2 hours | **Owner:** Whole team

### Steps
1. Script the 3-minute video with a strict time budget, e.g.:
   - 0:00–0:30 — problem + architecture (show the system diagram)
   - 0:30–1:30 — live dashboard: show device panel updating live, power meter, trigger/point out an alert
   - 1:30–2:30 — Discord bot: run `!status`, `!room`, `!usage` live, show a proactive alert if implemented
   - 2:30–3:00 — quick mention of schematic + wrap-up
2. Before recording, force at least one alert condition ahead of time (per the Risks section in the blueprint) so the Alerts Panel isn't empty on camera.
3. Do one full dry run without recording to check timing.
4. Record, trim, and export; upload per submission instructions.
5. Do a final repo check: all diagrams committed, README accurate, no leftover debug console logs cluttering a live terminal shown on screen.

### Exit Criteria
- [ ] Video is ≤3 minutes, shows dashboard live-updating, bot responding, and briefly explains architecture
- [ ] At least one alert is visibly triggered and shown in both the dashboard and (if built) the bot
- [ ] Final repo pushed, README and diagrams all present and accurate

### Pitfalls
- Recording before forcing a demo-friendly alert condition — an empty Alerts Panel undersells the feature you spent real effort building.

---

## Quick Reference: Phase → Grading Weight Alignment

| Phase(s) | Primarily builds toward |
|---|---|
| 4, 5 | "Quality of demo & dummy data simulation" (15%) |
| 7 (frontend half) | "Working web dashboard with real-time data" (20%) + "Dashboard visuals and UX quality" (10%) |
| 7 (bot half), 6 | "Working Discord bot reflecting real simulated data" (10%) |
| 2 (diagram), separate schematic task | "System diagram" (15%) + "Circuit schematic" (15%) |
| 1, 8, 9 | "Well structured and documented codebase, commits" (15%) |

Use this table to sanity-check time allocation if you're running behind — don't let any 15%+ category go untouched.
