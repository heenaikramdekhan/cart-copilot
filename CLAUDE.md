
# AI Multi-Agent Shopping Assistant

A six-agent system that turns a plain-language shopping request into a real decision:
it parses intent, searches real stores live, compares products, summarizes real reviews, and —
the differentiator — **reasons over the whole cart** to catch savings, spec mismatches,
and shipping inefficiencies.

All product, price, and review data is real. There is no mock or synthetic data in this project.

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
| Database | Supabase (Postgres) |
| LLM | Gemini API — `gemini-2.5-flash` via the `google-genai` Python SDK |

## Layout

```
backend/
  app/
    main.py        FastAPI entrypoint
    config.py      env-backed settings
    api/           route modules (chat, cart)
    agents/        the six agents, one module each
    graph/         LangGraph state schema + graph builder
    services/      LLM client, Supabase client, store APIs, review corpus
    prompts/       prompt templates for the 3 LLM agents
  scripts/         one-off scripts (corpus ingest)
  tests/
frontend/
  src/
    api/           backend client
    components/    chat panel, comparison table, cart panel
    types/         shared TS types mirroring the agent state
data/
  raw/             Amazon Reviews 2023 shards (gitignored, large)
  seed/            schema.sql — review corpus + product-identity tables
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
| 2 | Product Search | live fan-out to eBay + Best Buy, normalize into candidate listings | No |
| 3 | Comparison | normalize specs, rank top 5 | No |
| 4 | Review Intelligence | real review text → pros/cons | Yes |
| 5 | **Cart Optimization** | rule checks → natural-language recommendation | Rules + LLM |
| 6 | Deal & Coupon | surface real markdowns and coupon availability reported by the store | No |

Agents 5 and 6 are independent and run as parallel branches in the graph.

## LLM notes

- Model: `gemini-2.5-flash` via the `google-genai` SDK. Chosen because Gemini's Flash tier is
  permanently free with no card — a cost constraint, not a capability judgement. Pro-class models
  left the free tier in April 2026.
- Every LLM call goes through `app/services/llm.py`. Swapping providers means changing that file
  and the three agent call sites, never the graph or the state schema.
- For structured output, pass the Pydantic model as `response_schema` with
  `response_mime_type="application/json"`, and read `response.parsed`. Do not parse JSON out of
  free text — a malformed answer should fail at the boundary, not downstream.
- Each agent's system prompt lives in its own module under `prompts/` so it stays a stable,
  reusable constant. Nothing per-request may be interpolated into it.
- Free tier is rate limited (requests per minute and per day). Batch or back off rather than
  retrying in a tight loop.

## Data sources

| Data | Source | Freshness |
|---|---|---|
| Listings, multi-seller prices, shipping | eBay Browse API (free, ~5k calls/day) | live per query |
| Prices, stock, star rating, review count | Best Buy Products API (free key) | live per query |
| Review **text** | Amazon Reviews 2023 (UCSD McAuley Lab) | static snapshot, ends Sept 2023 |

Products are joined across sources on **brand plus manufacturer model number** — the corpus
`Item model number` matched against eBay's `mpn`. Measured on a 4,000-item Electronics sample,
62.7% of items carry a model number and only 0.1% carry a UPC, so UPC/GTIN is stored when present
but nothing may depend on it. Never join on fuzzy title similarity — that silently attaches the
wrong reviews to a product.

Postgres holds the review corpus, not a product catalog. Products are fetched live; reviews are
retrieved by product identity (`where parent_asin = ...`), not by similarity — so there is no
embedding column and no pgvector. Add one only when a feature actually needs semantic search.

## Constraints worth remembering

- **No mock, dummy, or synthetic data anywhere.** If a real value is unavailable, omit the field and
  say so in the UI — do not fabricate a plausible one.
- No scraping. Amazon, Walmart, and Best Buy all prohibit it; the free APIs above are the only
  sanctioned path. This is what makes the project publicly deployable.
- Neither free API returns individual review text — only aggregate ratings. That is why review text
  comes from the static corpus. Keep the review source behind one interface so a paid live-review
  provider can be swapped in without touching the graph.
- Review text is real but up to ~2 years old. Label its recency wherever it surfaces.
- Not every product will have a review match. Surface match confidence; never invent coverage.
- Prices are USD from the source APIs.

## Locked category scope

Tiers 1–3 are in scope. The schema is category-agnostic; these tiers are a data decision.

- **Tier 1 — PC peripherals & components** (build first): laptops, monitors, keyboards, mice,
  headsets, docking stations, SSDs/RAM, routers. Chosen because model-number identity is reliable, both APIs
  carry it, Amazon Electronics is the deepest review corpus, and it is the only cluster with genuine
  cross-item compatibility rules for Agent 5 (refresh rate vs. GPU, dock vs. available ports,
  DDR4 vs. DDR5, same-seller shipping consolidation).
- **Tier 2 — phones, tablets, audio**: same join mechanics as Tier 1, no new engineering.
- **Tier 3 — home & kitchen appliances**: Best Buy coverage is partial here; expect eBay-only
  results for some items.

**Out of scope: furniture and other generic goods.** They lack UPCs and model numbers, so there is
no reliable key to join reviews to prices. Revisit only after Tiers 1–3 work end to end.
