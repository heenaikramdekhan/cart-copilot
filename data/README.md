# Data

`seed/` — the Phase 1 deliverables. Drop these here:

| File | Contents |
|---|---|
| `seed.sql` | Supabase schema (`stores`, `products`, `store_listings`) + inserts |
| `products.json` | 28 laptops, stratified by price tier and use case |
| `stores.json` | 4 mock stores with distinct pricing bias and shipping cost |
| `store_listings.json` | 77 cross-store listings, partial coverage (2–4 stores per product) |

`raw/` — source datasets (the Kaggle laptop specs). Gitignored; not needed to run the app.

Load into Supabase with the SQL editor, or `python backend/scripts/seed_db.py` once that exists.
