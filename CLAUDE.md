
# AI Multi-Agent Shopping Assistant

A six-agent system that turns a plain-language shopping request into a real decision:
it parses intent, searches mock stores, compares products, summarizes reviews, and —
the differentiator — **reasons over the whole cart** to catch savings, spec mismatches,
and shipping inefficiencies.

Full plan and scoping decisions: `docs/PROJECT_PLAN.md`.

## Working agreement

**Before any coding task, load the `andrej-karpathy-skills:karpathy-guidelines` skill and follow it.**
Its four rules govern all work in this repo:

1. **Think before coding** — state assumptions, surface tradeoffs, ask when unclear. Don't pick silently.
2. **Simplicity first** — minimum code that solves the problem. No speculative abstractions, no
   unrequested config knobs, no error handling for impossible cases.
3. **Surgical changes** — touch only what the request requires. Don't refactor adjacent code or
   "improve" formatting. Match existing style.
4. **Goal-driven execution** — restate the task as a verifiable success criterion before starting.

Project-specific corollaries:
- Only 3 of 6 agents call an LLM. Do not add LLM calls to the deterministic agents (Product Search,
  Comparison, Deal & Coupon) — that is a deliberate architectural choice, not an oversight.
- Agents communicate **only** through the shared state object. No free-text handoffs between agents.

## Stack

| Layer | Choice |
|---|---|
| Frontend | React 19 + TypeScript, Vite |
| Backend | FastAPI (Python 3.10+) |
| Orchestration | LangGraph |
| Database | Supabase (Postgres + pgvector) |
| LLM | Claude API — `claude-opus-4-8` via the `anthropic` Python SDK |

## Layout

```
backend/
  app/
    main.py        FastAPI entrypoint
    config.py      env-backed settings
    api/           route modules (chat, cart)
    agents/        the six agents, one module each
    graph/         LangGraph state schema + graph builder
    services/      Claude client, Supabase client, embeddings
    prompts/       prompt templates for the 3 LLM agents
  scripts/         one-off scripts (DB seeding, embedding generation)
  tests/
frontend/
  src/
    api/           backend client
    components/    chat panel, comparison table, cart panel
    types/         shared TS types mirroring the agent state
data/
  raw/             source datasets (gitignored)
  seed/            seed.sql, products.json, stores.json, store_listings.json
docs/
```

## Commands

```bash
# backend
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev          # http://localhost:5173
```

## The six agents

| # | Agent | Responsibility | LLM? |
|---|---|---|---|
| 1 | Requirement Analyzer | free text → budget, category, must-haves, nice-to-haves | Yes |
| 2 | Product Search | pgvector similarity search across store listings | No |
| 3 | Comparison | normalize specs, rank top 5 | No |
| 4 | Review Intelligence | review text → pros/cons | Yes |
| 5 | **Cart Optimization** | rule checks → natural-language recommendation | Rules + LLM |
| 6 | Deal & Coupon | match cart against per-store discount rules | No |

Agents 5 and 6 are independent and run as parallel branches in the graph.

## Claude API notes

- Model: `claude-opus-4-8`. Use `thinking={"type": "adaptive"}` for the reasoning-heavy agents
  (Requirement Analyzer, Cart Optimization narrative).
- `temperature` / `top_p` / `top_k` and `budget_tokens` are **rejected** on this model — do not
  add them. Control depth with `output_config={"effort": ...}`.
- For agents that must return structured data (Requirement Analyzer, Review Intelligence), use
  `client.messages.parse()` with a Pydantic model rather than parsing JSON out of free text.
- The system prompt for each agent is a stable prefix — mark it with `cache_control` so repeated
  turns hit the prompt cache.

## Constraints worth remembering

- Mock stores only. Live scraping of real retailers is out of scope (ToS + no open APIs).
- Review text is synthetically generated from spec thresholds — it is internally consistent with
  each product's specs by construction. Do not mix in externally-sourced review data.
- Source pricing is in INR. Any currency conversion is a display concern, not a data concern.
- Battery life is a heuristic estimate, not sourced data. Label it as such anywhere it surfaces.
- Catalog is laptops only. Cross-category cart flags have no data to work with yet.
