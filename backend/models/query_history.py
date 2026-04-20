"""
QueryHistory model — stores every natural-language question + generated SQL + result.
"""

from datetime import datetime
from db.database import db


class QueryHistory(db.Model):
    __tablename__ = "query_history"

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    generated_sql = db.Column(db.Text, nullable=True)
    result_data = db.Column(db.JSON, nullable=True)    # list[dict] rows
    result_columns = db.Column(db.JSON, nullable=True) # list[str]
    row_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="success")  # success | error
    error_message = db.Column(db.Text, nullable=True)
    execution_time_ms = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "question": self.question,
            "generated_sql": self.generated_sql,
            "result_data": self.result_data,
            "result_columns": self.result_columns,
            "row_count": self.row_count,
            "status": self.status,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat(),
        }
