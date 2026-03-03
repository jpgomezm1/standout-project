# StandOut — Operational Event Orchestrator

Event-driven orchestration layer for short-term rental operations. Converts unstructured human input (audio, images, text via Telegram) into structured operational events.

## Structure

```
/backend    — FastAPI async backend (Python 3.12)
/frontend   — Next.js 14 dashboard (TypeScript)
```

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # fill in values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` at the project root.
