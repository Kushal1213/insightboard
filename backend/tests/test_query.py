"""
Tests — query validation, SQL injection prevention, schema safety.
Run with: pytest tests/test_query.py -v
"""

import pytest
from pydantic import ValidationError

# ── Import the modules under test ──────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from schemas.schemas import QueryRequest
from services.ai_service import validate_generated_sql


# ═══════════════════════════════════════════════════════════════════════════════
# QueryRequest schema validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestQueryRequestSchema:

    def test_valid_request(self):
        req = QueryRequest(question="Show top 5 customers", dataset_id=1)
        assert req.question == "Show top 5 customers"
        assert req.dataset_id == 1

    def test_question_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(question="Hi", dataset_id=1)
        assert "min_length" in str(exc_info.value) or "least" in str(exc_info.value)

    def test_question_too_long(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="x" * 501, dataset_id=1)

    def test_invalid_dataset_id_zero(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show all rows", dataset_id=0)

    def test_invalid_dataset_id_negative(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show all rows", dataset_id=-5)

    def test_missing_question(self):
        with pytest.raises(ValidationError):
            QueryRequest(dataset_id=1)

    def test_missing_dataset_id(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show me something")

    # SQL injection inside the question field
    def test_sql_injection_semicolon(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show all; DROP TABLE users", dataset_id=1)

    def test_sql_injection_comment(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show all -- bypass", dataset_id=1)

    def test_sql_injection_exec(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="exec(rm -rf /)", dataset_id=1)

    def test_sql_injection_multiline_comment(self):
        with pytest.raises(ValidationError):
            QueryRequest(question="Show /* comment */ everything", dataset_id=1)

    def test_whitespace_is_stripped(self):
        req = QueryRequest(question="  Who are the top customers?  ", dataset_id=1)
        assert req.question == "Who are the top customers?"


# ═══════════════════════════════════════════════════════════════════════════════
# Generated SQL safety validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateGeneratedSQL:

    def test_valid_simple_select(self):
        sql = "SELECT id, name FROM ds_sales LIMIT 10"
        ok, reason = validate_generated_sql(sql)
        assert ok is True

    def test_valid_aggregate(self):
        sql = "SELECT category, COUNT(*) FROM ds_products GROUP BY category LIMIT 50"
        ok, reason = validate_generated_sql(sql)
        assert ok is True

    def test_valid_order_by(self):
        sql = "SELECT name, revenue FROM ds_sales ORDER BY revenue DESC LIMIT 5"
        ok, reason = validate_generated_sql(sql)
        assert ok is True

    def test_rejects_delete(self):
        sql = "DELETE FROM ds_sales WHERE id = 1"
        ok, reason = validate_generated_sql(sql)
        assert ok is False
        assert "DELETE" in reason.upper() or "SELECT" in reason

    def test_rejects_update(self):
        sql = "UPDATE ds_sales SET revenue = 0 WHERE id = 1"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_rejects_drop(self):
        sql = "DROP TABLE ds_sales"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_rejects_insert(self):
        sql = "INSERT INTO ds_sales VALUES (1, 'x', 100)"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_rejects_alter(self):
        sql = "ALTER TABLE ds_sales ADD COLUMN hacked TEXT"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_rejects_multiple_statements(self):
        sql = "SELECT * FROM ds_sales LIMIT 10; DROP TABLE ds_sales"
        ok, reason = validate_generated_sql(sql)
        assert ok is False
        assert "semicolon" in reason.lower() or "Multiple" in reason

    def test_rejects_exec(self):
        sql = "EXEC xp_cmdshell('whoami')"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_case_insensitive_delete(self):
        sql = "delete from ds_sales where id = 1"
        ok, reason = validate_generated_sql(sql)
        assert ok is False

    def test_trailing_semicolon_allowed(self):
        sql = "SELECT * FROM ds_sales LIMIT 10;"
        ok, reason = validate_generated_sql(sql)
        assert ok is True


# ═══════════════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_empty_sql(self):
        ok, reason = validate_generated_sql("")
        assert ok is False

    def test_whitespace_only_sql(self):
        ok, reason = validate_generated_sql("   ")
        assert ok is False

    def test_select_with_subquery(self):
        sql = "SELECT * FROM (SELECT id FROM ds_sales LIMIT 5) sub LIMIT 5"
        ok, reason = validate_generated_sql(sql)
        assert ok is True  # subqueries are fine as long as parent is SELECT
