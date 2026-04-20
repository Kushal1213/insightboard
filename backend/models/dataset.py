"""
Dataset model — represents an uploaded CSV file.
"""

from datetime import datetime
from db.database import db


class Dataset(db.Model):
    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    row_count = db.Column(db.Integer, default=0)
    column_names = db.Column(db.JSON, nullable=False)   # list[str]
    column_types = db.Column(db.JSON, nullable=False)   # {col: dtype}
    table_name = db.Column(db.String(100), unique=True, nullable=False)  # SQL table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    queries = db.relationship("QueryHistory", backref="dataset", lazy=True,
                              cascade="all, delete-orphan")
    widgets = db.relationship("Widget", backref="dataset", lazy=True,
                              cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "filename": self.filename,
            "row_count": self.row_count,
            "column_names": self.column_names,
            "column_types": self.column_types,
            "table_name": self.table_name,
            "created_at": self.created_at.isoformat(),
        }
