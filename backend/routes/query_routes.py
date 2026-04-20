"""
Query Routes — POST /api/query, GET /api/datasets/<id>/history
"""

import logging
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from schemas.schemas import QueryRequest
from services.query_service import QueryService

logger = logging.getLogger(__name__)
query_bp = Blueprint("query", __name__)
query_service = QueryService()


@query_bp.route("/query", methods=["POST"])
def run_query():
    """
    Accepts a natural-language question and returns query results.
    Body: { "question": str, "dataset_id": int }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON."}), 400

    # ── Pydantic validation ────────────────────────────────────────────────────
    try:
        req = QueryRequest(**body)
    except ValidationError as exc:
        errors = exc.errors()
        logger.warning("QueryRequest validation failed: %s", errors)
        return jsonify({
            "error": "Invalid request.",
            "detail": [
                {"field": e["loc"][-1], "message": e["msg"]} for e in errors
            ],
        }), 422

    try:
        history = query_service.run_question(
            question=req.question,
            dataset_id=req.dataset_id,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.exception("Unexpected error in run_query")
        return jsonify({"error": "Internal server error.", "detail": str(exc)}), 500

    if history.status == "error":
        return jsonify({
            "error": history.error_message,
            "query_id": history.id,
            "generated_sql": history.generated_sql,
        }), 422

    return jsonify({
        "query_id": history.id,
        "question": history.question,
        "generated_sql": history.generated_sql,
        "columns": history.result_columns or [],
        "rows": history.result_data or [],
        "row_count": history.row_count,
        "execution_time_ms": history.execution_time_ms,
    }), 200


@query_bp.route("/datasets/<int:dataset_id>/history", methods=["GET"])
def get_history(dataset_id: int):
    limit = min(int(request.args.get("limit", 50)), 200)
    history = query_service.get_history(dataset_id, limit=limit)
    return jsonify([h.to_dict() for h in history]), 200
