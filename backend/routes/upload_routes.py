"""
Upload Routes — POST /api/upload, GET /api/datasets, DELETE /api/datasets/<id>
"""

import logging
from flask import Blueprint, jsonify, request

from services.upload_service import UploadService

logger = logging.getLogger(__name__)
upload_bp = Blueprint("upload", __name__)
upload_service = UploadService()

ALLOWED_EXTENSIONS = {"csv"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_dataset():
    """
    Upload a CSV file and create a dataset.
    Multipart form-data: file field = 'file'
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are supported."}), 415

    try:
        dataset = upload_service.process_csv(file.stream, file.filename)
        logger.info("Upload successful: dataset id=%s", dataset.id)
        return jsonify({
            "message": "Dataset uploaded successfully.",
            **dataset.to_dict(),
        }), 201

    except ValueError as exc:
        logger.warning("Upload validation error: %s", exc)
        return jsonify({"error": str(exc)}), 422

    except RuntimeError as exc:
        logger.error("Upload runtime error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@upload_bp.route("/datasets", methods=["GET"])
def list_datasets():
    datasets = upload_service.get_all_datasets()
    return jsonify([d.to_dict() for d in datasets]), 200


@upload_bp.route("/datasets/<int:dataset_id>", methods=["GET"])
def get_dataset(dataset_id: int):
    try:
        dataset = upload_service.get_dataset(dataset_id)
        return jsonify(dataset.to_dict()), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@upload_bp.route("/datasets/<int:dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id: int):
    try:
        upload_service.delete_dataset(dataset_id)
        return jsonify({"message": f"Dataset {dataset_id} deleted."}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
