"""
Device simulator — APScheduler background jobs.

tick_devices(): randomly toggles 1–3 devices every SIMULATOR_TICK_SECONDS.
log_usage():    writes a total-wattage snapshot every USAGE_LOG_INTERVAL_SECONDS.

After each tick, the alert engine is evaluated and SocketIO events are emitted.
"""

import os
import random
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# These are imported inside functions to avoid circular imports at module load time.


def tick_devices(app):
    """Toggle 1–3 random devices and persist state changes."""
    with app.app_context():
        from .db import db
        from .models import Device
        from .realtime import emit_device_update
        from .services.alert_engine import evaluate
        from .services.usage_calculator import get_current_watts

        devices = Device.query.all()
        if not devices:
            return

        # Choose a random subset (1–3) of devices to toggle
        num_to_toggle = random.randint(1, min(3, len(devices)))
        chosen = random.sample(devices, num_to_toggle)
        now = datetime.utcnow()

        for device in chosen:
            device.status = not device.status
            device.last_changed = now
            if device.status:
                device.on_since = now      # turned ON
            else:
                device.on_since = None     # turned OFF — clear on_since

        db.session.commit()

        # Emit live updates for each toggled device
        for device in chosen:
            emit_device_update(device)

        # Run alert engine after state changes (within same app context)
        new_alerts = evaluate()
        for alert in new_alerts:
            from .realtime import emit_alert_created
            emit_alert_created(alert)

        # Calculate and emit real-time usage metrics to synchronize all clients instantly
        from .services.usage_calculator import get_per_room_watts, get_today_kwh
        from .realtime import emit_usage_update
        total = get_current_watts()
        per_room = get_per_room_watts()
        today_kwh = get_today_kwh()

        emit_usage_update(
            total_watts=total,
            per_room=per_room,
            today_kwh=today_kwh
        )

        print(f"[Simulator] Tick — {num_to_toggle} device(s) toggled | Total: {total}W")


def log_usage(app):
    """Write a wattage snapshot to usage_log."""
    with app.app_context():
        from .db import db
        from .models import UsageLog
        from .services.usage_calculator import get_current_watts

        total = get_current_watts()
        entry = UsageLog(timestamp=datetime.utcnow(), total_watts=total)
        db.session.add(entry)
        db.session.commit()
        print(f"[Simulator] Usage logged: {total}W at {entry.timestamp.isoformat()}")


def start_scheduler(app):
    """Create and start the APScheduler with both jobs."""
    tick_interval = int(os.getenv("SIMULATOR_TICK_SECONDS", 15))
    log_interval = int(os.getenv("USAGE_LOG_INTERVAL_SECONDS", 300))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=tick_devices,
        args=[app],
        trigger="interval",
        seconds=tick_interval,
        id="tick_devices",
    )
    scheduler.add_job(
        func=log_usage,
        args=[app],
        trigger="interval",
        seconds=log_interval,
        id="log_usage",
    )
    scheduler.start()
    print(f"[Simulator] Started — tick every {tick_interval}s, log every {log_interval}s")
    return scheduler
