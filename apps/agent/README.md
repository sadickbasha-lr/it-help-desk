# IT Help Desk ADK Agent — Phase 3

An [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) agent that
manages IT help-desk tickets through the Phase 2 REST API deployed on Google Cloud Run.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  User / Client                                       │
│  (chat UI, API, curl, ADK Dev UI)                   │
└─────────────────────────┬───────────────────────────┘
                          │ ADK /run endpoint (JSON)
                          ▼
┌─────────────────────────────────────────────────────┐
│  ADK Agent  (Cloud Run — it-help-desk-agent)        │
│  • Gemini 2.0 Flash                                  │
│  • tools: list_tickets, get_ticket, create_ticket   │
│            update_ticket, add_comment               │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP (API_BASE_URL)
                          ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2 REST API  (Cloud Run — it-help-desk-api)   │
│  GET /tickets          POST /tickets                │
│  GET /tickets/:id      PATCH /tickets/:id           │
│  POST /tickets/:id/comments                         │
└─────────────────────────┬───────────────────────────┘
                          │ SQL
                          ▼
┌─────────────────────────────────────────────────────┐
│  Cloud SQL PostgreSQL                                │
└─────────────────────────────────────────────────────┘
```

---

## Directory structure

```
apps/agent/
├── __init__.py       # package entry-point — exports root_agent
├── agent.py          # ADK Agent definition
├── prompts.py        # System prompt / instructions
├── tools.py          # API tool wrappers (one function per endpoint)
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container definition for GCP deployment
├── deploy.sh         # One-command GCP build + deploy script
├── .env.example      # Environment variable reference
└── README.md         # This file
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Python 3.12+ | |
| `google-adk` ≥ 1.0 | `pip install google-adk` |
| Phase 2 API deployed | Cloud Run URL required |
| Gemini API key **or** ADC | For local dev or GCP service account |

---

## Local development

### 1. Clone and install

```bash
cd apps/agent
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set API_BASE_URL and GOOGLE_API_KEY
```

### 3. Run the agent (ADK Dev UI)

```bash
adk web
```

Open http://localhost:8000 in your browser. Select the `it_help_desk_agent` and start chatting.

### 4. Run the agent (CLI)

```bash
adk run agent
```

### 5. Run the agent as an API server

```bash
adk api_server --port 8080 --agent agent
```

Then send a request:

```bash
curl -s -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"message": "List all open tickets", "session_id": "test-1"}'
```

---

## Testing the tools directly

You can test the tool wrappers without the agent by running the smoke test:

```bash
API_BASE_URL=https://your-cloud-run-url.run.app python -m pytest tests/ -v
```

Or run the smoke script manually:

```bash
API_BASE_URL=https://your-cloud-run-url.run.app python tests/smoke_test.py
```

---

## Docker (local)

```bash
# Build
docker build -t it-help-desk-agent:local .

# Run
docker run --rm \
  -p 8080:8080 \
  -e API_BASE_URL=https://your-cloud-run-url.run.app \
  -e GOOGLE_API_KEY=your_key \
  it-help-desk-agent:local
```

---

## GCP Deployment

### Option A — deploy.sh (recommended)

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1
export API_BASE_URL=https://it-help-desk-api-xxxxx-uc.a.run.app
export GOOGLE_API_KEY=AIza...   # omit if using Workload Identity

chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Authenticate Docker with Artifact Registry
2. Build and push the image
3. Deploy the service to Cloud Run
4. Print the service URL

### Option B — manual gcloud commands

```powershell
# Windows PowerShell
$PROJECT_ID="your-project"
$REGION="us-central1"
$REPO_NAME="it-help-desk"
$IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/it-help-desk-agent:latest"
$API_BASE_URL="https://it-help-desk-api-xxxxx-uc.a.run.app"
$GOOGLE_API_KEY="AIza..."

gcloud auth configure-docker "$REGION-docker.pkg.dev"
docker build -t $IMAGE .
docker push $IMAGE
gcloud run deploy it-help-desk-agent `
  --image $IMAGE `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars "API_BASE_URL=$API_BASE_URL,GOOGLE_API_KEY=$GOOGLE_API_KEY"
```

---

## End-to-end test against Cloud Run

Once both services are deployed, test the full chain:

```bash
AGENT_URL=https://it-help-desk-agent-xxxxx-uc.a.run.app

# List tickets
curl -s -X POST $AGENT_URL/run \
  -H "Content-Type: application/json" \
  -d '{"message": "List all tickets", "session_id": "e2e-1"}' | jq .

# Create a ticket
curl -s -X POST $AGENT_URL/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a ticket: My laptop screen is broken, high priority", "session_id": "e2e-1"}' | jq .

# Get a ticket
curl -s -X POST $AGENT_URL/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me ticket 1", "session_id": "e2e-1"}' | jq .
```

---

## Environment variables reference

| Variable | Required | Description |
|---|---|---|
| `API_BASE_URL` | **Yes** | Base URL of the Phase 2 Cloud Run API |
| `GOOGLE_API_KEY` | Dev only | Gemini API key (not needed on GCP with ADC) |
| `GOOGLE_CLOUD_PROJECT` | Optional | GCP project — auto-detected on Cloud Run |
| `PORT` | Optional | HTTP port (default 8080, injected by Cloud Run) |
