"""
Query Service — orchestrates AI SQL generation → safe execution → persistence.
"""

import logging
import time
from typing import Any, Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db.database import db
from models.dataset import Dataset
from models.query_history import QueryHistory
from services.ai_service import generate_sql, validate_generated_sql

logger = logging.getLogger(__name__)


class QueryService:

    def run_question(
        self, question: str, dataset_id: int
    ) -> QueryHistory:
        """
        Full pipeline:
        1. Load dataset metadata
        2. Ask AI to generate SQL
        3. Validate SQL (safety check)
        4. Execute against the dataset's dynamic table
        5. Persist QueryHistory record
        6. Return the record
        """
        # ── 1. Dataset lookup ──────────────────────────────────────────────────
        dataset: Dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        logger.info(
            "Processing question for dataset '%s' (id=%s): %s",
            dataset.name, dataset_id, question,
        )

        generated_sql = None
        error_msg = None
        rows: List[Dict[str, Any]] = []
        columns: List[str] = []
        start_ms = time.time()

        try:
            # ── 2. AI SQL generation ───────────────────────────────────────────
            generated_sql = generate_sql(
                question=question,
                table_name=dataset.table_name,
                column_types=dataset.column_types,
            )
            logger.info("Generated SQL: %s", generated_sql)

            # ── 3. Double-check validation (defence-in-depth) ──────────────────
            is_safe, reason = validate_generated_sql(generated_sql)
            if not is_safe:
                raise ValueError(f"SQL safety check failed: {reason}")

            # ── 4. Execute ─────────────────────────────────────────────────────
            rows, columns = self._execute_sql(generated_sql)
            status = "success"
            logger.info("Query returned %d rows.", len(rows))

        except ValueError as exc:
            error_msg = str(exc)
            status = "error"
            logger.error("Query validation error: %s", error_msg)

        except SQLAlchemyError as exc:
            error_msg = f"Database error: {exc}"
            status = "error"
            logger.error("SQLAlchemy error during query execution: %s", exc)

        except Exception as exc:
            error_msg = f"Unexpected error: {exc}"
            status = "error"
            logger.exception("Unexpected error in QueryService.run_question")

        elapsed_ms = (time.time() - start_ms) * 1000

        # ── 5. Persist ─────────────────────────────────────────────────────────
        history = QueryHistory(
            dataset_id=dataset_id,
            question=question,
            generated_sql=generated_sql,
            result_data=rows,
            result_columns=columns,
            row_count=len(rows),
            status=status,
            error_message=error_msg,
            execution_time_ms=round(elapsed_ms, 2),
        )
        db.session.add(history)
        db.session.commit()
        logger.info(
            "QueryHistory saved (id=%s, status=%s, %.1f ms).",
            history.id, status, elapsed_ms,
        )

        return history

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _execute_sql(
        self, sql: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Execute a pre-validated SELECT query using a raw SQLAlchemy connection.
        Returns (rows_as_dicts, column_names).
        """
        with db.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return rows, columns

    def get_history(
        self, dataset_id: int, limit: int = 50
    ) -> List[QueryHistory]:
        return (
            QueryHistory.query
            .filter_by(dataset_id=dataset_id)
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
            .all()
        )
