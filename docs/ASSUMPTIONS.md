# Assumptions

This document records deliberate decisions made on ambiguous requirements.

## Device Count: 15 vs 18

The problem brief contains a discrepancy between 15 and 18 total devices.

**Decision**: We are using **15 devices** — 2 fans + 3 lights × 3 rooms.

**Rationale**: The breakdown of 2 fans + 3 lights per room (5 × 3 = 15) is internally consistent with the per-device listing in the brief. The number 18 appears to be a typo.

This decision is reflected in `backend/app/db.py` (seed data) and in all API responses.

---

## Office Hours Window

**Decision**: Office hours are defined as **9:00 AM – 5:00 PM** (local server time).

Any device with `status = TRUE` outside this window triggers a **Rule A (after-hours)** alert.

Configurable via `OFFICE_HOURS_START` and `OFFICE_HOURS_END` environment variables.

---

## Prolonged Room-On Threshold

**Decision**: The threshold for Rule B is **2 hours continuous on-time**.

"Continuously on" requires that ALL devices in a room have `status = TRUE` AND each device's `on_since` timestamp is more than 2 hours in the past.

---

## Simulator Tick Interval

**Decision**: Default tick interval is **15 seconds** (configurable via `SIMULATOR_TICK_SECONDS`).

For the demo recording, this can be shortened to make visible changes appear faster.

---

## Single Source of Truth

Both the web dashboard and the Discord bot read exclusively from the Flask REST API backed by MySQL. No client-side mock data or separate in-memory stores exist.
