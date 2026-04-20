# InsightBoard — AI Prompt Rules

These rules are injected into every AI prompt for SQL generation.
They act as a hard constraint layer on top of the LLM output.

## Mandatory Rules

1. **SELECT only** — The AI MUST generate only `SELECT` statements.
   - Never generate: `DELETE`, `UPDATE`, `INSERT`, `DROP`, `ALTER`, `TRUNCATE`, `EXEC`, `EXECUTE`, `CREATE`, `REPLACE`, `MERGE`, `GRANT`, `REVOKE`.

2. **Row limit** — Every query MUST include `LIMIT 100` unless the user explicitly requests fewer rows.

3. **Schema-bound** — Only use column names that exist in the provided schema. Never fabricate columns.

4. **No subquery injection** — Do not construct queries that embed raw user-supplied strings as SQL fragments.

5. **No system tables** — Never query `pg_catalog`, `information_schema`, or any internal database metadata tables.

6. **Single statement** — Return exactly one SQL statement. No semicolons mid-query. No stacked queries.

7. **Aggregations allowed** — `GROUP BY`, `ORDER BY`, `HAVING`, `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` are all permitted.

8. **JOINs** — Allowed only within the current dataset's table. Do not JOIN to external or system tables.

9. **Output format** — Return raw SQL only. No markdown code fences, no explanatory text, no comments.

## Examples of Allowed Queries

```sql
SELECT customer_name, SUM(revenue) AS total_revenue
FROM ds_sales_abc12345
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 10
```

```sql
SELECT product_category, COUNT(*) AS count
FROM ds_sales_abc12345
GROUP BY product_category
LIMIT 100
```

## Examples of Forbidden Queries

```sql
-- FORBIDDEN: modifies data
DELETE FROM ds_sales_abc12345 WHERE id = 1;

-- FORBIDDEN: accesses system tables
SELECT * FROM pg_catalog.pg_tables;

-- FORBIDDEN: no LIMIT
SELECT * FROM ds_sales_abc12345;

-- FORBIDDEN: multiple statements
SELECT * FROM ds_sales_abc12345; DROP TABLE ds_sales_abc12345;
```
