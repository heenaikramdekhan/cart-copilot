# AI Multi-Agent Shopping Assistant — Project Plan

## 1. Concept

A user types a plain-language request:

> "I need a gaming laptop under $900 with at least 16GB RAM and good battery life."

Instead of returning a list of search results, six cooperating agents understand the request,
search across multiple mock stores, compare real options, summarize reviews, and — most
importantly — actively reason over the user's cart to catch savings, mismatches, and better
purchasing strategies.

## 2. Why this beats a typical shopping chatbot

Most "AI shopping assistants" only answer questions — search bars with a chat interface on top.
This system is built to make decisions:

- Understands real intent (budget, must-haves, nice-to-haves), not just keywords
- Searches and compares across multiple stores instead of one
- Summarizes reviews instead of making the user read them
- **Actively reasons over the whole cart** — cheaper equivalents, spec mismatches, shipping-cost
  inefficiencies across stores
- Surfaces deals and bundle discounts automatically

The cart optimization agent (Agent 5) is the differentiator. Review summarization and product
recommendation are increasingly common; an agent that reasons across the entire cart for savings
and compatibility issues is not.

## 3. Architecture

Layers, top to bottom:

1. **Frontend** — React + TypeScript: chat UI, cart view, comparison table
2. **Backend API** — session state, cart CRUD, endpoint that runs the agent graph
3. **LangGraph orchestrator** — routes one shared state object through the six agents
4. **Data & AI** — mock store DB (Supabase Postgres + pgvector) and the Claude API, used only
   where real reasoning is needed

### The six agents

| # | Agent | Responsibility | LLM? |
|---|---|---|---|
| 1 | Requirement Analyzer | extracts budget, category, must-haves, nice-to-haves from free text | Yes |
| 2 | Product Search | embedding similarity search across mock store listings | No |
| 3 | Comparison | normalizes specs, ranks top 5 | No |
| 4 | Review Intelligence | summarizes into pros/cons | Yes |
| 5 | **Cart Optimization** | rule checks (duplicates, compatibility, shipping consolidation) turned into a natural-language recommendation | Rules + LLM |
| 6 | Deal & Coupon | matches cart against each store's discount rules | No |

Only 3 of 6 agents need an LLM call. This is deliberate: it keeps the multi-agent architecture
honest (tools + reasoning, not LLM calls end to end) and keeps the system cheaper and more testable.

### Shared agent state

One JSON object flows through the graph. Each agent reads its section and writes its own — no
free-text handoffs.

```json
{
  "user_query": "gaming laptop under $900...",
  "requirements": { "category": "laptop", "budget": 900, "must_have": ["16GB RAM"], "nice_to_have": ["good battery"] },
  "search_results": ["...raw listings across stores..."],
  "ranked_products": ["...top 5, normalized spec fields..."],
  "review_summaries": { "product_id": { "pros": [], "cons": [] } },
  "cart": ["...items with store_id, price..."],
  "cart_flags": ["similar mouse for $45 saves $35"],
  "deals": ["...bundle/coupon matches..."]
}
```

## 4. Phases

### Phase 0 — Scope lock ✅
- Category for MVP: laptops only (schema is category-agnostic, so phones/headphones can be added later)
- Mock stores: 4
- Dataset: hybrid — real laptop specs from a public Kaggle dataset, synthetic review text generated
  from spec thresholds (avoids entity-resolution between unrelated spec and review datasets)
- Team: solo. Timeline: no fixed deadline; first milestone is "laptops working end to end"

### Phase 1 — Data layer ✅
- `seed.sql` — Supabase schema (`stores`, `products`, `store_listings`) + inserts
- `products.json` — 28 laptops, stratified across budget/mid/premium/high-end and
  gaming/general/productivity, with a category-agnostic `attributes` JSONB field and
  spec-grounded synthetic review summaries
- `stores.json` — 4 mock stores with distinct pricing bias and shipping costs
- `store_listings.json` — 77 cross-store listings with realistic price variation, partial store
  coverage per product (2–4 of 4), stock levels, occasional discounts

**Known gap:** catalog is laptops only, so cross-category cart flags ("gaming laptop + 60Hz monitor
mismatch") have no data yet. Same-category logic (duplicate item, cheaper equivalent elsewhere,
shipping consolidation) is fully testable. A small accessories set can be added later on the same schema.

### Phase 2 — Agent state schema & Requirement Analyzer ← next
- Finalize the shared state JSON schema
- Build and test Agent 1 against 10–15 varied queries

### Phase 3 — Remaining agents
Product Search → Comparison → Review Intelligence → Cart Optimization → Deal & Coupon.
Each independently testable before moving on.

### Phase 4 — Orchestration
Wire the six agents into a LangGraph graph. Cart Optimization and Deal & Coupon run as parallel
branches — neither depends on the other's output.

### Phase 5 — Backend API
- `POST /api/chat` — runs the agent graph for a turn
- `GET /api/cart/:session_id`, `POST /api/cart/:session_id/items` — cart CRUD, kept separate from chat

### Phase 6 — Frontend
Chat panel, comparison table, cart panel with inline suggestion chips from `cart_flags`. Built last,
once there is real data and working agents to connect to.

### Phase 7 — Evaluation
- 15–20 test queries with known correct top picks → Requirement Analyzer + Comparison accuracy
- 3–5 deliberately planted suboptimal carts → prove Cart Optimization catches what it claims to
- Optional: small user study (5–10 people) vs. a plain single-store chatbot

## 5. Scoping decisions to state explicitly in any report

- Live scraping of real retailers isn't feasible — most prohibit it and don't offer open product
  APIs. Mock stores keep the focus on agent architecture rather than data access.
- Review text is synthetically generated from spec thresholds, not scraped — avoids an
  entity-resolution problem between separately-sourced spec and review datasets, and keeps review
  content internally consistent with each product's actual specs.
- Source pricing is in INR (the sourced dataset's native currency); USD conversion is a one-line change.
- Battery life is a synthetic estimate — the source dataset doesn't track it, but it was central to
  the original example scenario, so a heuristic estimate (GPU type, screen size, CPU class) was
  added and is clearly labeled as such.
