"""
Utility helpers for InsightBoard.
"""

import re


def safe_table_name(raw: str) -> str:
    """
    Convert an arbitrary string to a PostgreSQL-safe table name.
    Result is lowercase, max 50 chars, starts with a letter.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", raw.strip()).lower()[:50]
    if cleaned and cleaned[0].isdigit():
        cleaned = "t_" + cleaned
    return cleaned or "table"


def clamp(value: int, lo: int, hi: int) -> int:
    """Clamp value between lo and hi (inclusive)."""
    return max(lo, min(hi, value))


def paginate(query, page: int = 1, per_page: int = 50):
    """Return (items, total, pages) for a SQLAlchemy query."""
    page    = clamp(page, 1, 10_000)
    per_page = clamp(per_page, 1, 200)
    total   = query.count()
    items   = query.offset((page - 1) * per_page).limit(per_page).all()
    pages   = (total + per_page - 1) // per_page
    return items, total, pages
