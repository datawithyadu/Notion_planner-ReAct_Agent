# Notion_planner-ReAct_Agent
# Notion Planner — ReAct Agent

A ReAct (Reasoning + Acting) agent that manages Notion notes and calendar events through natural language, built with LangChain and served via a FastAPI backend with a custom chat UI. Fully containerized and deployed to AWS EC2 through an automated CI/CD pipeline.

**Live demo:** deployed on AWS EC2 (instance currently stopped when not in active use — see [Deployment](#deployment) for how to run it).

---

## What it does

Tell the agent what you want in plain English — "add a note that I finished the report" or "schedule gym at 6pm tomorrow" — and it reasons about which tool to call, executes it against your real Notion workspace, and confirms back to you.

**Tools available to the agent:**
- `get_notes` / `add_notes` / `trash_tool` / `find_tool` — manage Notion notes
- `get_event` / `new_event` / `trash_event` — manage Notion calendar events
- Weather lookup

---

## Architecture

```
Browser (chat UI)
      │  fetch('/chat')
      ▼
FastAPI (API/server.py)
      │
      ▼
ReAct Agent (Agent/bot.py)  ──uses──▶  Groq LLM (openai/gpt-oss-20b)
      │
      ▼
Notion Tools (tool/*.py)  ──calls──▶  Notion API
```

- **`Agent/bot.py`** — builds the LangChain ReAct agent from the tool list and system prompt; talks to Groq.
- **`API/server.py`** — FastAPI app exposing `/`, `/health`, and `/chat` (POST). Uses a `lifespan` context manager to build the agent once at startup.
- **`API/main.py`** — entrypoint that loads `.env` and starts Uvicorn.
- **`tool/`** — individual Notion/weather tool functions the agent can call.
- **`utils/logger.py`** — shared logging setup.
- **`static/`** — hand-built dark-theme chat UI (vanilla HTML/CSS/JS).

---

## Tech stack

| Layer | Tool |
|---|---|
| LLM | Groq (`openai/gpt-oss-20b`) |
| Agent framework | LangChain (ReAct pattern) |
| API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS |
| Containerization | Docker |
| Image registry | GitHub Container Registry (GHCR) |
| CI/CD | GitHub Actions |
| Hosting | AWS EC2 (Ubuntu) |

---

## Running locally

```bash
git clone https://github.com/datawithyadu/Notion_planner-ReAct_Agent.git
cd Notion_planner-ReAct_Agent
uv sync
```

Create a `.env` file with:
```
GROQ_API_KEY=your_key
NOTION_API_KEY=your_key
```

Run:
```bash
uv run python -m API.main
```

Visit `http://localhost:8000`.

---

## Running with Docker

```bash
docker build -t react-agent .
docker run --env-file .env -p 8000:8000 react-agent
```

---

## Deployment

This project deploys to AWS EC2 via a GitHub Actions pipeline (`.github/workflows/deploy.yml`) that runs on every push to `main`:

1. **`build-and-push`** — builds the Docker image and pushes it to GHCR.
2. **`deploy`** — SSHes into the EC2 instance, pulls the new image, and restarts the container.

**To run this yourself:**
- Launch an Ubuntu EC2 instance with Docker installed, open port `8000` in its security group.
- Place a `.env` file (Groq + Notion keys) on the instance at `~/.env`.
- Add these repo secrets under Settings → Secrets and variables → Actions:
  - `EC2_HOST` — the instance's public IP
  - `EC2_SSH_KEY` — the private key contents for SSH access
  - `GHCR_TOKEN` — a GitHub PAT with `repo` + `workflow` scopes (for pulling the image on the instance)
- Push to `main`.

> Note: EC2 assigns a new public IP each time the instance restarts (no Elastic IP attached), so `EC2_HOST` needs updating after a stop/start cycle.

---

## Postmortem — known failure modes & fixes in progress

Built as project 1 of a portfolio series aimed at business-facing AI / AI-consultant roles, with an explicit focus on evaluating agent reliability, cost, and trustworthiness rather than just "does it run."

**Failures observed during testing:**

1. **Reasoning repetition loop** — on a complex multi-step request, the model got stuck repeating the same self-check reasoning dozens of times, hit a token/length limit, and silently left part of the request undone with no error surfaced to the user. *Reliability + cost issue.*
2. **Redundant duplicate tool calls** — the same tool was called twice with identical arguments, gaining no new information but consuming tokens and contributing to rate-limit pressure. *Cost issue — wasted, zero-value actions.*
3. **False completion claims** — an early version of the agent narrated a confident, detailed "done" summary of actions it never actually took (no tool calls were made). A user trusting that response without checking Notion would believe things were done that weren't. *Trust issue.*

**Fixes designed (in progress):**
- A verification step after write actions (e.g. re-calling `get_event` to confirm a created event actually exists) before reporting success to the user.
- A system prompt rule requiring the agent's stated "success" language to be grounded in actual tool output, not free-form narration.

Full baseline measurement (test queries, per-run results, and the next single change to prioritize) is being tracked separately as part of an ongoing evaluation process.

---

## Roadmap context

This is project 1 of a 10-project portfolio series building toward AI consultant / business-facing AI specialist roles.
