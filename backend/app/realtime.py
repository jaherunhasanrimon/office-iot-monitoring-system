"""
Flask-SocketIO instance and event emitter helpers.
Import `socketio` here to avoid circular imports.
"""

from flask_socketio import SocketIO

socketio = SocketIO()


def emit_device_update(device):
    """Broadcast a device state change to all connected dashboard clients."""
    socketio.emit("device_update", device.to_dict())


def emit_alert_created(alert):
    """Broadcast a new alert to all connected dashboard clients."""
    socketio.emit("alert_created", alert.to_dict())


def emit_usage_update(total_watts, per_room, today_kwh):
    """Broadcast the updated power usage metrics to all clients."""
    socketio.emit("usage_update", {
        "total_watts": total_watts,
        "per_room": per_room,
        "estimated_kwh": today_kwh
    })
