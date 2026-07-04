"""
SQLAlchemy models: Room, Device, Alert, UsageLog
"""

from datetime import datetime
from .db import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    devices = db.relationship("Device", backref="room", lazy=True)
    alerts = db.relationship("Alert", backref="room", lazy=True, foreign_keys="Alert.room_id")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "fan" or "light"
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    status = db.Column(db.Boolean, default=False)          # True = ON
    power_watts = db.Column(db.Integer, nullable=False)    # fan ~60W, light ~15W
    last_changed = db.Column(db.DateTime, default=datetime.utcnow)
    on_since = db.Column(db.DateTime, nullable=True)       # SET on ON, NULL on OFF

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "room_id": self.room_id,
            "room_name": self.room.name if self.room else None,
            "status": self.status,
            "power_watts": self.power_watts,
            "last_changed": self.last_changed.isoformat() if self.last_changed else None,
            "on_since": self.on_since.isoformat() if self.on_since else None,
        }


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)        # "after_hours" | "prolonged_room_on"
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)    # NULL = still active

    device = db.relationship("Device", backref="alerts", foreign_keys=[device_id])

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "room_id": self.room_id,
            "device_id": self.device_id,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": self.resolved_at is None,
        }


class UsageLog(db.Model):
    __tablename__ = "usage_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_watts = db.Column(db.Integer, nullable=False)    # snapshot of total active wattage

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "total_watts": self.total_watts,
        }
