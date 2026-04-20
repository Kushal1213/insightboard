"""
Pydantic schemas — interface safety layer.
All incoming request bodies are validated here before reaching services.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ─── Upload ───────────────────────────────────────────────────────────────────

class DatasetUploadResponse(BaseModel):
    id: int
    name: str
    row_count: int
    column_names: List[str]
    column_types: Dict[str, str]
    table_name: str
    message: str


# ─── Query ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Validated request body for POST /api/query."""
    question: str = Field(..., min_length=3, max_length=500)
    dataset_id: int = Field(..., gt=0)

    @field_validator("question")
    @classmethod
    def no_sql_injection_in_question(cls, v: str) -> str:
        # Block obvious injection attempts inside the natural-language field
        forbidden = [";", "--", "/*", "*/", "xp_", "exec(", "execute("]
        lower = v.lower()
        for token in forbidden:
            if token in lower:
                raise ValueError(
                    f"Question contains forbidden token: '{token}'"
                )
        return v.strip()


class QueryResponse(BaseModel):
    query_id: int
    question: str
    generated_sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float


# ─── Widget ───────────────────────────────────────────────────────────────────

class WidgetCreateRequest(BaseModel):
    query_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    chart_type: Literal["bar", "line", "pie", "table"] = "bar"
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        # Strip any HTML tags from widget titles
        clean = re.sub(r"<[^>]+>", "", v)
        return clean.strip()


class WidgetResponse(BaseModel):
    id: int
    title: str
    chart_type: str
    config: Dict[str, Any]
    data_snapshot: List[Dict[str, Any]]
    position: int
    created_at: str


class DashboardResponse(BaseModel):
    dataset_id: int
    dataset_name: str
    widgets: List[WidgetResponse]


# ─── History ──────────────────────────────────────────────────────────────────

class HistoryItemResponse(BaseModel):
    id: int
    question: str
    generated_sql: str
    row_count: int
    status: str
    execution_time_ms: Optional[float]
    created_at: str


# ─── Generic ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
