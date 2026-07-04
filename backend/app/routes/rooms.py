from flask import Blueprint, jsonify, abort
from ..models import Room

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/api/rooms")
def get_all_rooms():
    rooms = Room.query.all()
    result = []
    for room in rooms:
        r = room.to_dict()
        r["devices"] = [d.to_dict() for d in room.devices]
        r["total_watts"] = sum(d.power_watts for d in room.devices if d.status)
        result.append(r)
    return jsonify(result), 200


@rooms_bp.route("/api/rooms/<string:room_name>")
def get_room(room_name):
    # Normalize input: lowercase, strip, remove hyphens and spaces for flexible matching
    normalized = room_name.strip().lower().replace("-", "").replace(" ", "")
    all_rooms = Room.query.all()

    def db_normalized(name):
        return name.lower().replace(" ", "").replace("-", "")

    def db_alias(name):
        # Strip the word "room" from the normalized DB name so
        # "workroom1" → "work1", "drawingroom" → "drawing"
        return db_normalized(name).replace("room", "")

    # Pass 1: exact normalized match  (e.g. "drawing room" → "drawingroom")
    room = next((r for r in all_rooms if db_normalized(r.name) == normalized), None)

    # Pass 2: alias match — strip "room" from DB name  (e.g. "work1" matches "Work Room 1")
    if not room:
        room = next((r for r in all_rooms if db_alias(r.name) == normalized), None)

    # Pass 3: partial LIKE match on original input
    if not room:
        like_normalized = room_name.strip().lower().replace("-", " ")
        room = Room.query.filter(Room.name.ilike(f"%{like_normalized}%")).first()

    if not room:
        return jsonify({"error": f"Room '{room_name}' not found."}), 404

    r = room.to_dict()
    r["devices"] = [d.to_dict() for d in room.devices]
    r["total_watts"] = sum(d.power_watts for d in room.devices if d.status)
    return jsonify(r), 200
