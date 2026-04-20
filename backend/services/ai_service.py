"""
AI Service — generates safe SQL from natural language questions.

Uses the Anthropic Claude API (falls back to a mock if no key is set).
Enforces prompt_rules.md constraints before execution.
"""

import logging
import os
import re
from typing import Dict, List, Tuple

import anthropic

logger = logging.getLogger(__name__)

# ─── Load prompt rules ────────────────────────────────────────────────────────
_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "ai", "prompt_rules.md")

def _load_rules() -> str:
    try:
        with open(_RULES_PATH) as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("prompt_rules.md not found — using inline fallback rules.")
        return (
            "Only generate SELECT statements. "
            "Never use DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE, or EXEC. "
            "Always add LIMIT 100 unless the user requests fewer rows. "
            "Use only columns that exist in the provided schema."
        )

PROMPT_RULES = _load_rules()


# ─── Safety validator ─────────────────────────────────────────────────────────

FORBIDDEN_SQL_KEYWORDS = re.compile(
    r"\b(DELETE|UPDATE|INSERT|DROP|ALTER|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE"
    r"|CREATE|REPLACE|MERGE|CALL|LOAD|COPY)\b",
    re.IGNORECASE,
)

def validate_generated_sql(sql: str) -> Tuple[bool, str]:
    """
    Returns (is_safe: bool, reason: str).
    Validates AI-generated SQL before it ever touches the database.
    """
    stripped = sql.strip()

    if not stripped.upper().startswith("SELECT"):
        return False, "Query must start with SELECT."

    if FORBIDDEN_SQL_KEYWORDS.search(stripped):
        match = FORBIDDEN_SQL_KEYWORDS.search(stripped)
        return False, f"Forbidden keyword detected: {match.group()}"

    if ";" in stripped[:-1]:  # allow trailing semicolon only
        return False, "Multiple statements are not allowed (semicolon found)."

    return True, "ok"


# ─── System prompt builder ────────────────────────────────────────────────────

def build_system_prompt(table_name: str, columns: Dict[str, str]) -> str:
    schema_lines = "\n".join(
        f"  - {col} ({dtype})" for col, dtype in columns.items()
    )
    return f"""You are a precise SQL generation assistant for the InsightBoard analytics platform.

## STRICT RULES (MUST FOLLOW)
{PROMPT_RULES}

## DATABASE SCHEMA
Table name: `{table_name}`
Columns:
{schema_lines}

## OUTPUT FORMAT
Return ONLY the raw SQL query — no markdown, no explanation, no backticks.
The query MUST be a SELECT statement.
Always include LIMIT 100 unless the user specifies a smaller number.
"""


# ─── Main generation function ─────────────────────────────────────────────────

def generate_sql(
    question: str,
    table_name: str,
    column_types: Dict[str, str],
) -> str:
    """
    Call Claude to generate SQL, then validate the output.
    Raises ValueError if the generated SQL fails safety checks.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — returning mock SQL.")
        return _mock_sql(table_name, column_types)

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = build_system_prompt(table_name, column_types)

    logger.info("Calling Claude API for SQL generation. Question: %s", question)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    raw_sql = message.content[0].text.strip()
    logger.info("Claude returned SQL: %s", raw_sql)

    # ── Post-generation safety check ─────────────────────────────────────────
    is_safe, reason = validate_generated_sql(raw_sql)
    if not is_safe:
        logger.error("AI-generated SQL failed safety check: %s | SQL: %s", reason, raw_sql)
        raise ValueError(f"Generated SQL failed safety validation: {reason}")

    return raw_sql


def _mock_sql(table_name: str, column_types: Dict[str, str]) -> str:
    """Fallback SQL when no API key is configured (demo / testing)."""
    cols = list(column_types.keys())
    select_cols = ", ".join(cols[:6]) if cols else "*"
    return f"SELECT {select_cols} FROM {table_name} LIMIT 10"
