"""
Dashboard Routes — GET /api/dashboard/<dataset_id>, POST /api/widgets, DELETE /api/widgets/<id>
"""

import logging
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from schemas.schemas import WidgetCreateRequest
from services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint("dashboard", __name__)
dashboard_service = DashboardService()


@dashboard_bp.route("/dashboard/<int:dataset_id>", methods=["GET"])
def get_dashboard(dataset_id: int):
    try:
        data = dashboard_service.get_dashboard(dataset_id)
        return jsonify(data), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@dashboard_bp.route("/widgets", methods=["POST"])
def create_widget():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON."}), 400

    try:
        req = WidgetCreateRequest(**body)
    except ValidationError as exc:
        return jsonify({
            "error": "Invalid widget request.",
            "detail": [
                {"field": e["loc"][-1], "message": e["msg"]} for e in exc.errors()
            ],
        }), 422

    try:
        widget = dashboard_service.create_widget(
            query_id=req.query_id,
            title=req.title,
            chart_type=req.chart_type,
            config=req.config or {},
        )
        return jsonify(widget.to_dict()), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@dashboard_bp.route("/widgets/<int:widget_id>", methods=["DELETE"])
def delete_widget(widget_id: int):
    try:
        dashboard_service.delete_widget(widget_id)
        return jsonify({"message": f"Widget {widget_id} deleted."}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@dashboard_bp.route("/dashboard/<int:dataset_id>/reorder", methods=["PUT"])
def reorder_widgets(dataset_id: int):
    body = request.get_json(silent=True) or {}
    ordered_ids = body.get("ordered_ids", [])
    if not isinstance(ordered_ids, list):
        return jsonify({"error": "ordered_ids must be a list."}), 400
    dashboard_service.reorder_widgets(dataset_id, ordered_ids)
    return jsonify({"message": "Widgets reordered."}), 200
