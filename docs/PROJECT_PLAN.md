# AI Multi-Agent Shopping Assistant — Project Plan

## 1. Concept

A user types a plain-language request:

> "I need a gaming laptop under $900 with at least 16GB RAM and good battery life."

Instead of returning a list of search results, six cooperating agents understand the request,
search live across multiple real stores, compare real options, summarize real reviews, and — most
importantly — actively reason over the user's cart to catch savings, mismatches, and better
purchasing strategies.

All data is real. No mock stores, no synthetic reviews.

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
4. **Data & AI** — live store APIs (eBay Browse, Best Buy) for products and prices, a stored real
   review corpus in Supabase Postgres, and the Gemini API, used only where real
   reasoning is needed

### The six agents

| # | Agent | Responsibility | LLM? |
|---|---|---|---|
| 1 | Requirement Analyzer | extracts budget, category, must-haves, nice-to-haves from free text | Yes |
| 2 | Product Search | live fan-out to eBay + Best Buy, normalized into candidate listings | No |
| 3 | Comparison | normalizes specs, ranks top 5 | No |
| 4 | Review Intelligence | summarizes into pros/cons | Yes |
| 5 | **Cart Optimization** | rule checks (duplicates, compatibility, shipping consolidation) turned into a natural-language recommendation | Rules + LLM |
| 6 | Deal & Coupon | surfaces real markdowns and coupon availability reported by the store | No |

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

### Phase 0 — Scope lock ✅ (revised — real data)
- Stores: real. eBay Browse API and Best Buy Products API, both free tiers, queried live per request.
- Reviews: real. Amazon Reviews 2023 (UCSD McAuley Lab) — 571M real reviews, free, static snapshot
  ending Sept 2023.
- Categories locked to Tiers 1–3 (below). Furniture and other generic goods are out of scope.
- Team: solo. Timeline: no fixed deadline; first milestone is "Tier 1 working end to end".

#### Locked category tiers
1. **PC peripherals & components** — laptops, monitors, keyboards, mice, headsets, docking stations,
   SSDs/RAM, routers. Built first.
2. **Phones, tablets, audio** — same join mechanics, no new engineering.
3. **Home & kitchen appliances** — Best Buy coverage is partial; some items will be eBay-only.

Selection criterion was **joinability**: reviews are ASIN-keyed and listings are keyed by
manufacturer part number, so a category only works when products carry a real model number.
Furniture fails this test, which is why it is deferred rather than included.

This choice also closes the old cross-category gap — Tier 1 has genuine compatibility rules for
Agent 5 (refresh rate vs. GPU class, dock vs. available ports, DDR4 vs. DDR5, same-seller shipping
consolidation).

### Phase 1 — Data layer ← next (redesign)

The previous mock-data deliverables (`products.json`, `stores.json`, `store_listings.json`) are
withdrawn. Replaced by:
- eBay + Best Buy API clients, normalized into one listing shape
- Amazon Reviews 2023 ingest for Tier 1 categories → Supabase, retrieved by product identity
- A product-identity table keyed on brand + model number, joining live listings to stored reviews
- A single review-source interface, so a paid live-review provider can be swapped in later without
  touching the agent graph

**Known limits, to be stated wherever they surface:** review text can be up to ~2 years old; not
every live listing will have a review match, so match confidence must be shown rather than implied.

### Phase 2 — Agent state schema & Requirement Analyzer
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

- **Prices and availability are live and real.** eBay and Best Buy both publish free official APIs;
  no scraping is involved, so the system is legally deployable to real users.
- **Review text is real but not live.** Neither free API exposes individual review text — only
  aggregate star ratings and counts. Live review text is available only from paid scraping
  services. The project therefore uses a large real review corpus (Amazon Reviews 2023) rather than
  fabricating review content. Recency is disclosed in the UI.
- **Deals come from the store, not from invented rules.** Real retailers do not publish coupon
  rules, so Agent 6 surfaces the markdown and coupon-availability data eBay already returns on a
  listing. The original mock-store design matched carts against discount rules written by hand;
  that had to change when the stores became real.
- **Products are matched on brand + model number, never on fuzzy title similarity.** Fuzzy title
  matching would silently attach the wrong product's reviews.
- **Categories are limited to Tiers 1–3 by joinability, not by ambition.** Generic goods such as
  furniture have no stable product identifier to join on.
- Pricing is USD, as returned by the source APIs.
- **The whole system runs at zero cost.** Gemini's Flash tier is permanently free with no card,
  and both data sources are free. The binding constraint is the free tier's rate limit — 5 requests
  per minute per model, and three LLM agents run per user query — not money.
- **Daraz was evaluated and excluded.** Daraz is the dominant marketplace in Pakistan, so it was
  the obvious candidate for a local-market version. Its Open Platform API is a *seller* API —
  create products, update prices, manage orders — and requires seller authorization; there is no
  public catalog-search endpoint, and no legal route to review text at all. The only sanctioned
  read path is the Involve Asia affiliate datafeed, which carries prices but not reviews. Adding
  Daraz would therefore mean scraping, which the project rules out. Because the store layer is
  built around one normalized `Listing` shape, adding Daraz later is a single new store client
  with no change to the agents.
