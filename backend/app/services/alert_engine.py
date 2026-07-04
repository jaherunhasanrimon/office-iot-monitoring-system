"""
Alert Rule Engine

Rule A — After-hours:
    Any device with status=True outside 9 AM–5 PM window.

Rule B — Prolonged room-on:
    ALL devices in a room have status=True AND on_since > 2 hours ago.

Deduplication: only creates a new alert if no unresolved alert of the same
type + scope (room/device) already exists.

Resolution: marks resolved_at when the condition no longer holds.
"""

import os
from datetime import datetime, timedelta
from ..db import db
from ..models import Device, Room, Alert


def _office_hours_start():
    return int(os.getenv("OFFICE_HOURS_START", 9))


def _office_hours_end():
    return int(os.getenv("OFFICE_HOURS_END", 17))


def _is_after_hours(now: datetime) -> bool:
    return now.hour < _office_hours_start() or now.hour >= _office_hours_end()


def _get_unresolved(alert_type: str, room_id=None, device_id=None):
    """Return an existing unresolved alert matching the given scope, or None."""
    q = Alert.query.filter_by(type=alert_type, resolved_at=None)
    if room_id is not None:
        q = q.filter_by(room_id=room_id)
    if device_id is not None:
        q = q.filter_by(device_id=device_id)
    return q.first()


def evaluate():
    """
    Run both alert rules. Called after every simulator tick.
    Must be called from within an active Flask app context.
    Returns a list of newly created Alert objects.
    """
    new_alerts = []
    now = datetime.utcnow()

    # ── Rule A: After-hours ───────────────────────────────────────────
    after_hours = _is_after_hours(now)
    all_devices = Device.query.all()

    for device in all_devices:
        existing = _get_unresolved("after_hours", device_id=device.id)

        if after_hours and device.status:
            if not existing:
                alert = Alert(
                    type="after_hours",
                    device_id=device.id,
                    room_id=device.room_id,
                    message=(
                        f"{device.name} in {device.room.name} is ON "
                        f"outside office hours."
                    ),
                    created_at=now,
                )
                db.session.add(alert)
                db.session.flush()
                new_alerts.append(alert)
        else:
            # Condition cleared → resolve
            if existing:
                existing.resolved_at = now

    # ── Rule B: Prolonged room-on (> 2 hrs continuous) ───────────────
    threshold = timedelta(hours=2)
    rooms = Room.query.all()

    for room in rooms:
        devices = room.devices
        if not devices:
            continue

        all_on = all(d.status for d in devices)
        all_long = all(
            d.on_since is not None and (now - d.on_since) >= threshold
            for d in devices
        )
        existing = _get_unresolved("prolonged_room_on", room_id=room.id)

        if all_on and all_long:
            if not existing:
                alert = Alert(
                    type="prolonged_room_on",
                    room_id=room.id,
                    message=(
                        f"All devices in {room.name} have been ON "
                        f"continuously for more than 2 hours."
                    ),
                    created_at=now,
                )
                db.session.add(alert)
                db.session.flush()
                new_alerts.append(alert)
        else:
            if existing:
                existing.resolved_at = now

    db.session.commit()
    return new_alerts
