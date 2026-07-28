# POC Agent SRE

A proof-of-concept SRE assistant: a FastAPI backend that triages incidents from logs, answers
operational questions grounded in a runbook ("skills") repo via an LLM with a React chat frontend..

## Architecture

```
frontend/   React + Vite + Tailwind chat UI
backend/    FastAPI app
  app/
    routers/    HTTP endpoints (chat, diagnose, health)
    services/   business logic (agent, skills repo, k8s deployment helpers)
    models/     Pydantic request/response schemas
    mcp_gateway.py   exposes the same tools over MCP (stdio)
  skills-repo/  Markdown "skills" (known failure patterns + runbooks)
k8s/        Kubernetes manifests for deploying backend + frontend
deploy-aks.ps1  Script to provision an Azure AKS cluster and deploy both services
```

## Features

- **`POST /chat`** — conversational endpoint. If `OPENAI_API_KEY` is set, questions are answered
  by an LLM (via LangChain) grounded only in the skills-repo runbooks and recently recorded
  incidents; otherwise it falls back to canned responses.
- **`POST /diagnose`** — pattern-matches a log/metric snippet against known failure signatures
  (OOM kill, connection refused, timeouts, 5xx, disk pressure) and returns severity, root cause,
  and recommended actions. Matches are recorded as incidents.
- **`GET /incidents`** — lists recorded incidents, most recent first.
- **`GET /health`** — liveness check.
- **MCP gateway** (`app/mcp_gateway.py`) — exposes `diagnose` and `list_incidents` as MCP tools
  for use from Claude Desktop/Claude Code.
- **Skills repo** (`backend/skills-repo/`) — Markdown runbooks with YAML front matter; see
  [backend/skills-repo/README.md](backend/skills-repo/README.md) for the schema. Edits take
  effect immediately since the backend reads the folder on each request.

## Prerequisites

- Python 3.12+
- [Bun](https://bun.sh/) (or Node.js/npm) for the frontend
- An OpenAI API key (optional — required only for LLM-backed chat responses)
- `kubectl` / `az` CLI (optional — only for Kubernetes/AKS deployment)

## Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then fill in OPENAI_API_KEY if you want LLM-backed chat
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://localhost:8000` (Swagger UI at `/docs`).

### Environment variables (`backend/.env`)

| Variable               | Default             | Purpose                                             |
|-------------------------|---------------------|------------------------------------------------------|
| `APP_NAME`              | `SRE Agent API`     | FastAPI app title                                     |
| `ENVIRONMENT`           | `development`       | Environment label                                     |
| `LOG_LEVEL`             | `INFO`               | Log verbosity                                         |
| `OPENAI_API_KEY`        | _(empty)_            | Enables LLM-backed `/chat` responses when set         |
| `OPENAI_MODEL`          | `gpt-4o-mini`        | Chat model used by LangChain                          |
| `SKILLS_REPO_PATH`      | `skills-repo`        | Path to the skills/runbooks folder                     |
| `MCP_DEPLOYMENT_NAMESPACE` | `mcp-deployment-space` | Kubernetes namespace used when creating new deployments |
| `DEPLOYMENTS_FILES_DIR` | `deployments`        | Where generated K8s manifest files are written locally |

### Running the MCP gateway standalone

```bash
cd backend
python -m app.mcp_gateway
```

## Frontend setup

```bash
cd frontend
bun install
bun run dev
```

The dev server runs on Vite's default port and talks to the backend at
`VITE_API_BASE_URL` (defaults to `http://localhost:8000`).

## Docker

Each service has its own `Dockerfile`:

```bash
docker build -t poc-agent-backend ./backend
docker build -t poc-agent-frontend ./frontend
```

## Example request

```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"source": "k8s-pod", "logs": "OutOfMemoryError: container killed"}'
```

See [example-question.json](example-question.json) for a sample `/chat` payload.

## Notes

This is a POC: incidents are stored in-memory (not persisted across restarts). Kubernetes
manifest generation (`app/services/new_deployment.py`) writes and applies files directly via
`kubectl` — the chat flow that would extract a deployment spec from a free-form message
(`spread_deployment_dto` in `app/services/agent_service.py`) is not implemented yet.
