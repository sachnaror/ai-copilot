# Enterprise AI Knowledge Copilot (Databricks + Mosaic AI)

## Problem Statement
Enterprise knowledge is fragmented across PDFs, Jira, Slack, APIs, and SQL systems. Keyword search misses intent and slows decisions.

## Solution
Production-style FastAPI copilot with Databricks-backed agentic RAG:
- Databricks Mosaic Vector Search retrieval
- Databricks Model Serving response generation
- UC Function-style tool calling through Databricks SQL Statements API
- JWT auth + RBAC (viewer/analyst/operator/admin)
- MLflow tracing + precision/recall evaluation
- Local-safe fallback mode for demo reliability

## Architecture
```text
User Browser/UI
    -> FastAPI (async + streaming)
    -> JWT Auth + RBAC
    -> MCP-Style Tool Router
    -> Databricks:
       - Vector Search (RAG)
       - Model Serving Endpoint
       - SQL Warehouse (UC function execution)
       - MLflow tracking
    -> Fallback: local mock retrieval + mock tool responses
```

## What Was Implemented
- FastAPI APIs:
  - `GET /` UI
  - `GET /dashboard` eval dashboard
  - `GET /auth/demo-token` quick demo token
  - `GET /auth/me` identity check
  - `POST /chat` protected chat
  - `POST /chat/stream` protected streaming chat
  - `POST /evaluate` admin-only golden dataset evaluation
- Databricks integration in `app/core/databricks.py`:
  - Vector Search query REST call
  - Model Serving invocations REST call
  - SQL statements execution + polling for UC-style tools
- JWT + RBAC:
  - Token create/decode
  - Route protection
  - Tool-level permission filtering
- Local demo UX:
  - UI auto-fetches token and calls protected APIs
  - `make dev-open` auto-opens browser
- DevOps:
  - Poetry (`pyproject.toml`)
  - `Makefile` targets
  - `poet` + `poet_install_make_dev.sh` bootstrap command
  - Dockerfile, docker-compose
  - ECS task definition template

## Local Demo Risks (Important)
1. If Databricks vars are missing/invalid, system falls back to mock responses (demo still works).
2. If valid Databricks creds are set but network blocks workspace access, calls gracefully fallback.
3. `POST /evaluate` needs `admin` role; dashboard handles this automatically.
4. First MLflow run creates local metadata, so first startup can be slightly slower.

## Setup (Poetry)
```bash
cd /Users/homesachin/Desktop/zoneone/practice/ai-copilot
cp .env.example .env
```

Optional: set real Databricks values in `.env`:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `DATABRICKS_VECTOR_SEARCH_INDEX`
- `DATABRICKS_MODEL_SERVING_ENDPOINT`
- `DATABRICKS_SQL_WAREHOUSE_ID`

## Your Requested Bootstrap Command
From project root:
```bash
./poet
```
This runs `poet_install_make_dev.sh`:
- configures Poetry env
- installs dependencies via `pyproject.toml`
- runs `make dev-open`

## Make Commands
```bash
make install      # poetry install
make dev          # run API server
make dev-open     # run server + open browser
make open         # open browser only
make evaluate     # run golden dataset eval script
make docker-build # build image
make docker-run   # run container locally
```

## Run Locally (Fast path)
```bash
cd /Users/homesachin/Desktop/zoneone/practice/ai-copilot
./poet
```

Manual alternative:
```bash
cd /Users/homesachin/Desktop/zoneone/practice/ai-copilot
poetry config --local virtualenvs.in-project true
poetry install
make dev-open
```

## 60-120 Second Interview Demo Flow
1. Open `http://127.0.0.1:8000/`.
2. Select role `analyst`, click `Get Demo Token`.
3. Ask: `Fetch Jira tickets for engineering project`.
4. Ask: `Run SQL to check latest timestamp`.
5. Open `http://127.0.0.1:8000/dashboard` and click `Run Evaluation`.
6. Mention fallback reliability and RBAC enforcement.

One-liner:

> I built a Databricks Mosaic AI agentic RAG copilot with Vector Search, UC-style tool calling, JWT RBAC, and MLflow evaluation for production-grade enterprise retrieval.
