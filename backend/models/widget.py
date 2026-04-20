"""
Widget model — a saved chart/table pinned to the dashboard.
"""

from datetime import datetime
from db.database import db


class Widget(db.Model):
    __tablename__ = "widgets"

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    query_id = db.Column(db.Integer, db.ForeignKey("query_history.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)   # bar | line | pie | table
    config = db.Column(db.JSON, nullable=False)             # axes, colors, etc.
    data_snapshot = db.Column(db.JSON, nullable=False)      # cached result rows
    position = db.Column(db.Integer, default=0)             # display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "query_id": self.query_id,
            "title": self.title,
            "chart_type": self.chart_type,
            "config": self.config,
            "data_snapshot": self.data_snapshot,
            "position": self.position,
            "created_at": self.created_at.isoformat(),
        }
