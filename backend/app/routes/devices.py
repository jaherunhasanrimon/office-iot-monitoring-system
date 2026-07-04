from flask import Blueprint, jsonify, abort
from ..models import Device

devices_bp = Blueprint("devices", __name__)


@devices_bp.route("/api/devices")
def get_all_devices():
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices]), 200


@devices_bp.route("/api/devices/<int:device_id>")
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict()), 200


@devices_bp.route("/api/devices/<int:device_id>/toggle", methods=["POST"])
def toggle_device(device_id):
    """Optional: manually toggle a device for demo control."""
    from datetime import datetime
    from ..db import db
    from ..realtime import emit_device_update

    device = Device.query.get_or_404(device_id)
    now = datetime.utcnow()
    device.status = not device.status
    device.last_changed = now
    device.on_since = now if device.status else None
    db.session.commit()
    emit_device_update(device)
    return jsonify(device.to_dict()), 200
