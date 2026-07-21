# AI Multi-Agent Shopping Assistant

Six cooperating agents turn a plain-language shopping request into a decision — parsing intent,
searching mock stores, comparing products, summarizing reviews, and reasoning over the whole cart
for savings and mismatches.

See [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) for the full plan and
[`CLAUDE.md`](CLAUDE.md) for the working agreement and architecture notes.

## Setup

**Backend** (Python 3.10+)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # then fill in the keys
uvicorn app.main:app --reload --port 8000
```

Check: <http://localhost:8000/api/health> returns `{"status":"ok"}`.

**Frontend** (Node 20+)

```bash
cd frontend
npm install
npm run dev
```

Runs on <http://localhost:5173>; `/api/*` is proxied to the backend.

**Database** — create a Supabase project, enable the `vector` extension, then run
`data/seed/seed.sql` in the SQL editor. See [`data/README.md`](data/README.md).

## Status

Phases 0 and 1 are done. Phase 2 (shared state schema + Requirement Analyzer) is next.
