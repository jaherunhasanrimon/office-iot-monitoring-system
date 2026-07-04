"""
Database initialisation and seeding.
Creates all tables and seeds 3 rooms + 15 devices on first run.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ── Seed data ────────────────────────────────────────────────────────────────

ROOMS = [
    {"id": 1, "name": "Drawing Room"},
    {"id": 2, "name": "Work Room 1"},
    {"id": 3, "name": "Work Room 2"},
]

# 2 fans + 3 lights per room = 15 devices total
DEVICES = [
    # Drawing Room (room_id=1)
    {"name": "Fan 1",   "type": "fan",   "room_id": 1, "power_watts": 60},
    {"name": "Fan 2",   "type": "fan",   "room_id": 1, "power_watts": 60},
    {"name": "Light 1", "type": "light", "room_id": 1, "power_watts": 15},
    {"name": "Light 2", "type": "light", "room_id": 1, "power_watts": 15},
    {"name": "Light 3", "type": "light", "room_id": 1, "power_watts": 15},
    # Work Room 1 (room_id=2)
    {"name": "Fan 3",   "type": "fan",   "room_id": 2, "power_watts": 60},
    {"name": "Fan 4",   "type": "fan",   "room_id": 2, "power_watts": 60},
    {"name": "Light 4", "type": "light", "room_id": 2, "power_watts": 15},
    {"name": "Light 5", "type": "light", "room_id": 2, "power_watts": 15},
    {"name": "Light 6", "type": "light", "room_id": 2, "power_watts": 15},
    # Work Room 2 (room_id=3)
    {"name": "Fan 5",   "type": "fan",   "room_id": 3, "power_watts": 60},
    {"name": "Fan 6",   "type": "fan",   "room_id": 3, "power_watts": 60},
    {"name": "Light 7", "type": "light", "room_id": 3, "power_watts": 15},
    {"name": "Light 8", "type": "light", "room_id": 3, "power_watts": 15},
    {"name": "Light 9", "type": "light", "room_id": 3, "power_watts": 15},
]


def init_db():
    """Create tables and seed initial data if the tables are empty."""
    from .models import Room, Device

    db.create_all()

    # Only seed if rooms table is empty
    if Room.query.count() == 0:
        for r in ROOMS:
            db.session.add(Room(id=r["id"], name=r["name"]))
        db.session.flush()

    if Device.query.count() == 0:
        for d in DEVICES:
            db.session.add(Device(
                name=d["name"],
                type=d["type"],
                room_id=d["room_id"],
                power_watts=d["power_watts"],
                status=False,
                last_changed=datetime.utcnow(),
                on_since=None,
            ))

    db.session.commit()
    print("[DB] Tables ready, seed data applied.")
