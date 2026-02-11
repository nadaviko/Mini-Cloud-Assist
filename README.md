# Mini-Cloud-Assist

A tiny, GitHub-ready demo that mirrors the fundamentals of "Gemini Cloud Assist":
- Ingest telemetry (logs + metrics)
- Build a grounded context snapshot
- Generate a root-cause hypothesis + confidence + next actions
- Serve via API and CLI

## Quickstart

### 1) Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
cp .env.example .env
