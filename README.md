# IT Help Desk — AI Ticketing System

> **Repository for the IT Help Desk Agent Project**

This repository is organised in phases:

| Phase | Description | Location |
|-------|-------------|----------|
| Phase 2 | REST API + Cloud SQL (deployed to Cloud Run) | `apps/api/` |
| Phase 3 | ADK Agent (deployed to Cloud Run) | `apps/agent/` |

---

## Phase 3 — ADK Agent (current)

An [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) agent built with
**Gemini 2.0 Flash** that gives users a natural-language interface to the Phase 2 ticketing API.

### Quick start (local)

```bash
cd apps/agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit API_BASE_URL and GOOGLE_API_KEY
adk web                # opens Dev UI at http://localhost:8000
```

### Deploy to GCP (Cloud Run)

```bash
export PROJECT_ID=your-project
export REGION=us-central1
export API_BASE_URL=https://it-help-desk-api-xxxxx-uc.a.run.app
export GOOGLE_API_KEY=AIza...
cd apps/agent && ./deploy.sh
```

See [`apps/agent/README.md`](apps/agent/README.md) for full documentation.

---

## Architecture

```
User / Client
    │ chat
    ▼
ADK Agent (Cloud Run)          ← Phase 3
    │ HTTP  API_BASE_URL
    ▼
REST API  (Cloud Run)          ← Phase 2
    │ SQL
    ▼
Cloud SQL PostgreSQL
```

---

## Phase 2 — REST API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/tickets` | List all tickets |
| GET | `/tickets/:id` | Get a ticket |
| POST | `/tickets` | Create a ticket |
| PATCH | `/tickets/:id` | Update a ticket |
| POST | `/tickets/:id/comments` | Add a comment |

---

## Running tests

```bash
# Phase 3 unit tests (no cloud services required)
cd it-help-desk
python -m pytest apps/agent/tests/ -v

# Phase 3 smoke tests (requires live API_BASE_URL)
API_BASE_URL=https://your-cloud-run-url.run.app \
  python apps/agent/tests/smoke_test.py
```
