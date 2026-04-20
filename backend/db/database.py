"""
Database initialisation — uses Flask-SQLAlchemy.
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app and create tables."""
    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy registers them before create_all
        from models.dataset import Dataset          # noqa: F401
        from models.query_history import QueryHistory  # noqa: F401
        from models.widget import Widget            # noqa: F401
        db.create_all()
        logger.info("Database tables created / verified.")
