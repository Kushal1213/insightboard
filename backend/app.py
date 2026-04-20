"""
InsightBoard — AI-Powered Analytics Dashboard Builder
Main Flask application entry point.
"""

import logging
import os
from flask import Flask
from flask_cors import CORS

from db.database import init_db
from routes.upload_routes import upload_bp
from routes.query_routes import query_bp
from routes.dashboard_routes import dashboard_bp

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("insightboard.log"),
    ],
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = "development") -> Flask:
    """Application factory pattern."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Config ────────────────────────────────────────────────────────────────
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/insightboard"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")

    # ── DB Init ───────────────────────────────────────────────────────────────
    init_db(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(query_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    logger.info("InsightBoard application created successfully.")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
