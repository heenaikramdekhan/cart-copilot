# Data

All data in this project is real. Nothing here is mock or synthetic.

## Where each piece comes from

| Data | Source | Fetched |
|---|---|---|
| Listings, multi-seller prices, shipping | eBay Browse API | live, per query |
| Prices, stock, star rating, review count | Best Buy Products API | live, per query |
| Review text | Amazon Reviews 2023 (UCSD McAuley Lab) | ingested once into Supabase |

Products and prices are **not** stored — they are fetched live, so nothing in this directory
describes a product catalog.

## Directories

`raw/` — downloaded Amazon Reviews 2023 shards for the Tier 1 categories. Large and gitignored;
needed only to run the ingest, not to run the app.

`seed/` — `schema.sql`: the review corpus table and the product-identity table that joins live
listings to stored reviews on brand + model number. There is no embedding column: reviews are
retrieved by product identity, not by similarity.

## Category scope

Ingest covers Tiers 1–3 only:

1. PC peripherals & components — laptops, monitors, keyboards, mice, headsets, docks, SSDs/RAM, routers
2. Phones, tablets, audio
3. Home & kitchen appliances

Furniture and other generic goods are out of scope — they carry no UPC or model number, so reviews
cannot be reliably joined to prices.

## Known limits

- Review text ends Sept 2023. It is real, but up to ~2 years old; surface this in the UI.
- Not every live listing will match a reviewed product. Show match confidence rather than implying
  full coverage.
- Never join on fuzzy title similarity. It attaches the wrong product's reviews.
