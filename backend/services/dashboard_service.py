"""
Dashboard Service — manages widgets pinned to the dashboard.
"""

import logging
from typing import Dict, Any, List

from db.database import db
from models.widget import Widget
from models.query_history import QueryHistory
from models.dataset import Dataset

logger = logging.getLogger(__name__)


class DashboardService:

    def create_widget(
        self,
        query_id: int,
        title: str,
        chart_type: str,
        config: Dict[str, Any],
    ) -> Widget:
        """Pin a query result as a dashboard widget."""
        query: QueryHistory = QueryHistory.query.get(query_id)
        if not query:
            raise ValueError(f"QueryHistory {query_id} not found.")
        if query.status != "success":
            raise ValueError("Cannot create widget from a failed query.")

        # Auto-suggest axes if config is empty
        if not config and query.result_columns:
            cols = query.result_columns
            config = {
                "x_axis": cols[0] if len(cols) > 0 else None,
                "y_axis": cols[1] if len(cols) > 1 else cols[0],
                "color": "#6366f1",
            }

        widget = Widget(
            dataset_id=query.dataset_id,
            query_id=query_id,
            title=title,
            chart_type=chart_type,
            config=config,
            data_snapshot=query.result_data or [],
            position=self._next_position(query.dataset_id),
        )
        db.session.add(widget)
        db.session.commit()
        logger.info("Widget '%s' (id=%s) created.", title, widget.id)
        return widget

    def get_dashboard(self, dataset_id: int) -> Dict[str, Any]:
        dataset: Dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        widgets: List[Widget] = (
            Widget.query
            .filter_by(dataset_id=dataset_id)
            .order_by(Widget.position.asc())
            .all()
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset.name,
            "widgets": [w.to_dict() for w in widgets],
        }

    def delete_widget(self, widget_id: int) -> None:
        widget: Widget = Widget.query.get(widget_id)
        if not widget:
            raise ValueError(f"Widget {widget_id} not found.")
        db.session.delete(widget)
        db.session.commit()
        logger.info("Widget %s deleted.", widget_id)

    def reorder_widgets(self, dataset_id: int, ordered_ids: List[int]) -> None:
        for position, widget_id in enumerate(ordered_ids):
            widget = Widget.query.filter_by(
                id=widget_id, dataset_id=dataset_id
            ).first()
            if widget:
                widget.position = position
        db.session.commit()
        logger.info("Widgets reordered for dataset %s.", dataset_id)

    @staticmethod
    def _next_position(dataset_id: int) -> int:
        last = (
            Widget.query
            .filter_by(dataset_id=dataset_id)
            .order_by(Widget.position.desc())
            .first()
        )
        return (last.position + 1) if last else 0
