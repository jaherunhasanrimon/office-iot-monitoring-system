from flask import Blueprint, jsonify
from ..services.usage_calculator import get_current_watts, get_per_room_watts, get_today_kwh

usage_bp = Blueprint("usage", __name__)


@usage_bp.route("/api/usage/current")
def current_usage():
    return jsonify({
        "total_watts": get_current_watts(),
        "per_room": get_per_room_watts(),
    }), 200


@usage_bp.route("/api/usage/today")
def today_usage():
    return jsonify({
        "estimated_kwh": get_today_kwh(),
    }), 200
