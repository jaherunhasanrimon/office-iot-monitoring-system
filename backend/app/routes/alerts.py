from flask import Blueprint, jsonify, request
from ..models import Alert

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/api/alerts")
def get_alerts():
    include_resolved = request.args.get("resolved", "false").lower() == "true"

    if include_resolved:
        alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    else:
        alerts = (
            Alert.query
            .filter_by(resolved_at=None)
            .order_by(Alert.created_at.desc())
            .all()
        )

    return jsonify([a.to_dict() for a in alerts]), 200
