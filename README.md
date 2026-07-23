# AI Multi-Agent Shopping Assistant

Six cooperating agents turn a plain-language shopping request into a decision — parsing intent,
searching real stores live, comparing products, summarizing real reviews, and reasoning over the
whole cart for savings and mismatches. All data is real; nothing is mocked.

See [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) for the full plan and
[`CLAUDE.md`](CLAUDE.md) for the working agreement and architecture notes.

## Live demo

**<https://cart-copilot-kohl.vercel.app>**

Frontend on Vercel, FastAPI backend on Render, review corpus on Supabase. The backend runs on a
free tier that sleeps when idle, so the first request after a quiet spell can take up to a minute
to wake; after that it is fast.

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

**Database** — create a Supabase project, then run
`data/seed/schema.sql` in the SQL editor. See [`data/README.md`](data/README.md).

## Status

Deployed and live (see above). All six agents run against real data. The review corpus holds
141,240 real reviews across ~5,600 products.

Product Search serves **catalog mode** — the ingested Amazon corpus priced from its Sept 2023
snapshot — until eBay's Buy API access is granted. The live eBay client is written and
OAuth-verified against production; it switches in through one environment variable, with no other
change. Deal & Coupon surfaces the store-reported discounts a listing carries.
