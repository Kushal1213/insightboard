# InsightBoard — AI Usage Policy (`agents.md`)

## Overview

InsightBoard uses AI (Anthropic Claude) exclusively for **natural-language to SQL translation**.
No other application logic is AI-driven.

---

## AI Usage Scope

| Feature              | AI Used? | Details                                      |
|----------------------|----------|----------------------------------------------|
| SQL generation       | ✅ Yes    | Claude converts user questions → SQL queries |
| CSV parsing          | ❌ No     | Handled by pandas deterministically          |
| Chart rendering      | ❌ No     | Recharts, pure frontend                      |
| Data storage         | ❌ No     | PostgreSQL, no AI involved                   |
| Authentication       | ❌ No     | (future work)                                |

---

## Safety Controls

### 1. Prompt-level constraints (`ai/prompt_rules.md`)
Every AI call includes a strict system prompt that:
- Restricts output to `SELECT` statements only
- Bans `DELETE`, `UPDATE`, `INSERT`, `DROP`, `ALTER`, `TRUNCATE`, `EXEC`, `CREATE`
- Mandates `LIMIT 100` on all results
- Restricts column references to the provided schema only
- Prohibits access to system/internal tables (`pg_catalog`, `information_schema`)

### 2. Post-generation validation (`services/ai_service.py`)
Before any AI output touches the database:
- Regex-based keyword scanner rejects forbidden SQL verbs
- Statement must begin with `SELECT`
- Multiple statements (`;` mid-query) are rejected

### 3. Input sanitisation (`schemas/schemas.py`)
User question strings are validated via Pydantic before reaching AI:
- Forbidden tokens: `;`, `--`, `/*`, `*/`, `exec(`, `execute(`
- Length limits enforced (3–500 characters)
- Whitespace stripped

### 4. Parameterisation layer
All AI-generated SQL is executed via SQLAlchemy's `text()` binding —
no raw string concatenation of user input into queries.

---

## Human Oversight

- All generated SQL is stored in `query_history` and visible in the History UI.
- Failed queries (rejected by safety checks) are logged with `status = "error"` and
  the `error_message` field, giving operators full auditability.
- No AI output is executed silently or without logging.

---

## Observability

All AI calls log:
- The question asked
- The generated SQL
- Whether the safety check passed or failed
- Execution time

Logs are written to `insightboard.log` and stdout via Python's `logging` module.

---

## Limitations & Tradeoffs

| Tradeoff                                 | Mitigation                               |
|------------------------------------------|------------------------------------------|
| LLM can hallucinate column names         | Schema is injected; validator rejects bad SQL |
| LLM may generate inefficient queries     | LIMIT 100 hard cap prevents runaway scans |
| No auth system yet                       | Noted as future work; datasets are open  |
| AI cost per query                        | Results are cached in `query_history`    |

---

## Model

- Provider: **Anthropic**
- Model: `claude-sonnet-4-20250514`
- Max tokens: 512 (SQL output is short)
- Temperature: default (0.0 effective — SQL generation benefits from determinism)
