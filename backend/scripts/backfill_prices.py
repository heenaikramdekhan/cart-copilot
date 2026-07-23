"""Backfill the products table with the corpus's snapshot price.

The original ingest stored product identity and rating but not price, because
products were meant to be priced live. Catalog mode needs a price, so this
streams the metadata once more and re-upserts each in-tier product — now
carrying the price product_from_meta extracts. Reviews are left untouched.

Run once, after `alter table products add column price numeric;`:

  python -m scripts.backfill_prices

This re-collects the in-tier product set, which is a superset of the pruned
table, so it re-adds products with too few reviews. Run data/seed/prune.sql
afterward to drop them again — the surviving products keep their new price.
"""

from scripts.ingest_reviews import collect_products, insert_products


def main() -> None:
    print("Scanning Electronics metadata for in-tier products (price pass)...")
    products = collect_products("Electronics", 20_000)
    priced = sum(1 for p in products.values() if p["price"] is not None)
    print(f"Upserting {len(products)} products ({priced} with a price)...")
    insert_products(list(products.values()))
    print("Done. Catalog mode can now price these products.")


if __name__ == "__main__":
    main()
