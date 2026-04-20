"""
Upload Service — parses uploaded CSV and creates a dynamic SQL table.
"""

import hashlib
import io
import logging
import re
import time
from typing import IO

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db.database import db
from models.dataset import Dataset

logger = logging.getLogger(__name__)

# Maximum rows allowed per upload
MAX_ROWS = 50_000


class UploadService:

    def process_csv(self, file_stream: IO[bytes], filename: str) -> Dataset:
        """
        1. Parse CSV with pandas
        2. Infer column types
        3. Create a dedicated SQL table for this dataset
        4. Bulk-insert rows
        5. Persist Dataset metadata
        """
        logger.info("Processing CSV upload: %s", filename)
        start = time.time()

        try:
            df = pd.read_csv(file_stream, nrows=MAX_ROWS)
        except Exception as exc:
            logger.error("Failed to parse CSV '%s': %s", filename, exc)
            raise ValueError(f"Could not parse CSV file: {exc}") from exc

        if df.empty:
            raise ValueError("Uploaded CSV is empty.")

        # ── Sanitise column names ──────────────────────────────────────────────
        df.columns = [self._safe_col(c) for c in df.columns]
        df = df.where(pd.notnull(df), None)  # NaN → None for JSON safety

        column_types = {col: str(df[col].dtype) for col in df.columns}
        column_names = list(df.columns)

        # ── Generate a unique table name ───────────────────────────────────────
        hash_suffix = hashlib.md5(
            (filename + str(time.time())).encode()
        ).hexdigest()[:8]
        base = re.sub(r"[^a-z0-9]", "_", filename.lower().replace(".csv", ""))[:30]
        table_name = f"ds_{base}_{hash_suffix}"

        # ── Create SQL table and insert rows ───────────────────────────────────
        try:
            df.to_sql(
                table_name,
                db.engine,
                if_exists="replace",
                index=False,
                chunksize=500,
            )
            logger.info(
                "Inserted %d rows into table '%s'.", len(df), table_name
            )
        except SQLAlchemyError as exc:
            logger.error("DB error creating table '%s': %s", table_name, exc)
            raise RuntimeError(f"Database error during upload: {exc}") from exc

        # ── Save Dataset record ────────────────────────────────────────────────
        dataset = Dataset(
            name=filename.replace(".csv", ""),
            filename=filename,
            row_count=len(df),
            column_names=column_names,
            column_types=column_types,
            table_name=table_name,
        )
        db.session.add(dataset)
        db.session.commit()

        elapsed = (time.time() - start) * 1000
        logger.info(
            "Dataset '%s' (id=%s) created in %.1f ms.", dataset.name, dataset.id, elapsed
        )
        return dataset

    def get_all_datasets(self):
        return Dataset.query.order_by(Dataset.created_at.desc()).all()

    def get_dataset(self, dataset_id: int) -> Dataset:
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")
        return dataset

    def delete_dataset(self, dataset_id: int) -> None:
        dataset = self.get_dataset(dataset_id)
        # Drop the dynamic table
        with db.engine.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{dataset.table_name}"'))
            conn.commit()
        db.session.delete(dataset)
        db.session.commit()
        logger.info("Dataset %s and table '%s' deleted.", dataset_id, dataset.table_name)

    @staticmethod
    def _safe_col(name: str) -> str:
        """Convert any column header to a safe SQL identifier."""
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", str(name).strip())
        if safe[0].isdigit():
            safe = "col_" + safe
        return safe.lower()
