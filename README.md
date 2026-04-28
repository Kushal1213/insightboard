# InsightBoard

> **Mini Power BI + AI** — Upload a CSV, ask questions in plain English, get SQL-powered charts instantly.

-----

## Problem

Business users struggle to extract insights from raw CSV data without knowing SQL.
Existing tools either require technical expertise (SQL editors) or cost hundreds of dollars per seat (Tableau, Power BI).

## Solution

InsightBoard lets anyone upload a CSV and ask questions like:
- *"Show top 5 customers by revenue"*
- *"Count orders grouped by product category"*
- *"What was the average sale amount last month?"*

The AI translates questions into validated SQL, executes them safely, and renders the results as interactive charts or tables that can be pinned to a personal dashboard.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React 18, Vite, Tailwind CSS, Recharts |
| Backend    | Python 3.11, Flask 3, Flask-SQLAlchemy |
| Database   | PostgreSQL 15                     |
| AI         | Anthropic Claude (`claude-sonnet-4-20250514`) |
| Validation | Pydantic v2                       |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   React Frontend                │
│  Pages: Home · Dataset · Dashboard · History   │
│  Components: ChartPreview · ResultTable        │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/JSON  (Vite proxy → :5000)
┌──────────────────▼──────────────────────────────┐
│                  Flask API                      │
│  Routes:  /api/upload  /api/query  /api/dashboard│
│  Services: UploadService · QueryService         │
│            AiService · DashboardService         │
│  Schemas:  Pydantic validation layer            │
└──────────┬──────────────────────────────────────┘
           │ SQLAlchemy ORM / raw text()
┌──────────▼──────────────────────────────────────┐
│               PostgreSQL                        │
│  Tables: datasets · query_history · widgets     │
│  + dynamic tables: ds_<name>_<hash>             │
└─────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────┐
│           Anthropic Claude API                  │
│  Input:  schema + prompt_rules.md + question    │
│  Output: validated SELECT SQL only              │
└─────────────────────────────────────────────────┘
```

---

## Project Structure

```
insightboard/
├── backend/
│   ├── app.py                   # Flask app factory
│   ├── routes/
│   │   ├── upload_routes.py     # POST /upload, GET /datasets
│   │   ├── query_routes.py      # POST /query, GET /history
│   │   └── dashboard_routes.py  # GET /dashboard, POST /widgets
│   ├── services/
│   │   ├── upload_service.py    # CSV parsing → dynamic SQL table
│   │   ├── query_service.py     # AI → SQL → execute → persist
│   │   ├── ai_service.py        # Claude API + safety validation
│   │   └── dashboard_service.py # Widget CRUD
│   ├── models/
│   │   ├── dataset.py
│   │   ├── query_history.py
│   │   └── widget.py
│   ├── schemas/
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── db/
│   │   └── database.py          # SQLAlchemy init
│   ├── ai/
│   │   └── prompt_rules.md      # Injected into every AI prompt
│   ├── tests/
│   │   └── test_query.py        # pytest suite
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── pages/
│   │   │   ├── HomePage.jsx     # CSV upload + dataset list
│   │   │   ├── DatasetPage.jsx  # AI query interface
│   │   │   ├── DashboardPage.jsx# Widget grid
│   │   │   └── HistoryPage.jsx  # Query log
│   │   ├── components/
│   │   │   ├── layout/Layout.jsx
│   │   │   ├── charts/ChartPreview.jsx  # Bar/Line/Pie via Recharts
│   │   │   └── ui/ResultTable.jsx
│   │   └── services/api.js      # Axios service layer
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── README.md
└── agents.md                    # AI usage policy
```

---

## Setup & Running

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15 running locally

### 1. Database

```bash
psql -U postgres -c "CREATE DATABASE insightboard;"
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set DATABASE_URL and ANTHROPIC_API_KEY

python app.py
# → Flask running on http://localhost:5000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → React running on http://localhost:3000
```

### 4. Run Tests

```bash
cd backend
pytest tests/test_query.py -v
```

---

## API Reference

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/upload`                     | Upload CSV (multipart/form-data)   |
| GET    | `/api/datasets`                   | List all datasets                  |
| GET    | `/api/datasets/:id`               | Get single dataset                 |
| DELETE | `/api/datasets/:id`               | Delete dataset + its SQL table     |
| POST   | `/api/query`                      | Run natural language query         |
| GET    | `/api/datasets/:id/history`       | Query history for a dataset        |
| GET    | `/api/dashboard/:id`              | Get all widgets for a dataset      |
| POST   | `/api/widgets`                    | Pin query result as widget         |
| DELETE | `/api/widgets/:id`                | Remove widget                      |
| PUT    | `/api/dashboard/:id/reorder`      | Reorder widgets                    |

---

## AI Usage

Claude is used **only for SQL generation**. Every call:

1. Includes `prompt_rules.md` as a system constraint (SELECT-only, LIMIT 100, schema-bound).
2. Has its output validated by a regex safety scanner before execution.
3. Is logged to `query_history` with full auditability.

See [`agents.md`](./agents.md) for the full AI usage policy.

---

## Validation & Security

- **Pydantic schemas** validate all incoming request bodies (types, lengths, forbidden tokens).
- **SQL injection in question field** is blocked at the schema layer (`;`, `--`, `/*` rejected).
- **Generated SQL** is scanned for forbidden keywords before DB execution.
- **Parameterised execution** via SQLAlchemy `text()` — no raw string concatenation.
- **Dynamic table names** use a hash suffix to prevent collisions and guessing.

---

## Observability

Python `logging` is configured at app startup:

```python
logging.info("Query executed: %s rows in %.1f ms", row_count, elapsed_ms)
logging.error("Safety check failed: %s | SQL: %s", reason, sql)
```

All logs go to stdout **and** `insightboard.log`.

---

## Tradeoffs

| Decision                     | Tradeoff                                               |
|------------------------------|--------------------------------------------------------|
| AI-generated SQL             | Hallucination risk — mitigated by schema injection + validation |
| Dynamic SQL tables per CSV   | Flexible but requires cleanup on dataset delete        |
| No auth system (v1)          | Simpler to demo; production would need JWT / sessions  |
| LIMIT 100 hard cap           | Prevents performance issues; limits large exports      |
| Single-model AI              | No fallback if Claude API is down; could add OpenAI    |

---

## Future Work

- User authentication (JWT)
- Real-time dashboard auto-refresh (WebSockets)
- Multi-file joins
- Natural language chart customisation ("make the bars blue")
- Export dashboard as PDF
- Scheduled query alerts
