"""
Usage Calculator

get_current_watts():  SUM of power_watts for all devices currently ON.
get_per_room_watts(): Per-room wattage breakdown.
get_today_kwh():      Estimated kWh since OFFICE_HOURS_START today,
                      using trapezoidal integration of usage_log snapshots.
"""

import os
from datetime import datetime, timedelta
from ..db import db
from ..models import Device, Room, UsageLog


def get_current_watts() -> int:
    """Return total wattage of all currently ON devices."""
    devices = Device.query.filter_by(status=True).all()
    return sum(d.power_watts for d in devices)


def get_per_room_watts() -> list:
    """Return per-room wattage breakdown."""
    rooms = Room.query.all()
    result = []
    for room in rooms:
        watts = sum(
            d.power_watts for d in room.devices if d.status
        )
        result.append({"room_id": room.id, "room_name": room.name, "watts": watts})
    return result


def get_today_kwh() -> float:
    """
    Estimate today's kWh usage using the trapezoidal rule over usage_log rows
    since OFFICE_HOURS_START (default 9 AM) today.
    """
    start_hour = int(os.getenv("OFFICE_HOURS_START", 9))
    now = datetime.utcnow()
    day_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)

    if now < day_start:
        return 0.0

    logs = (
        UsageLog.query
        .filter(UsageLog.timestamp >= day_start)
        .order_by(UsageLog.timestamp.asc())
        .all()
    )

    if not logs:
        return 0.0

    # Trapezoidal integration: Σ (watts_i + watts_i+1) / 2 × Δt_hours
    kwh = 0.0
    for i in range(1, len(logs)):
        dt_hours = (logs[i].timestamp - logs[i - 1].timestamp).total_seconds() / 3600
        avg_watts = (logs[i].total_watts + logs[i - 1].total_watts) / 2
        kwh += avg_watts * dt_hours / 1000  # convert W·h → kWh

    return round(kwh, 4)
