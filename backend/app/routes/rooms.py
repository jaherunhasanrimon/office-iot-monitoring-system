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
    # Case-insensitive name match (strip spaces, lowercase)
    normalized = room_name.strip().lower().replace("-", " ")
    room = Room.query.filter(
        Room.name.ilike(f"%{normalized}%")
    ).first()

    if not room:
        return jsonify({"error": f"Room '{room_name}' not found."}), 404

    r = room.to_dict()
    r["devices"] = [d.to_dict() for d in room.devices]
    r["total_watts"] = sum(d.power_watts for d in room.devices if d.status)
    return jsonify(r), 200
