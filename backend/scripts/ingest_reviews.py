"""Ingest a bounded slice of the Amazon Reviews 2023 corpus into Supabase.

Neither corpus file supports random access, so the passes are ordered by cost.
Metadata comes first and stops as soon as enough Tier 1 candidates are found —
a small read, because roughly a quarter of Electronics items qualify. Reviews
are then streamed as a bounded prefix, keeping only those belonging to a
candidate.

Candidates that end up with too few reviews are deleted at the end: a product
Agent 4 cannot summarize is not worth storing.

  python scripts/ingest_reviews.py                       # defaults below
  python scripts/ingest_reviews.py --max-review-gb 1     # quick trial run
"""

import argparse
import json
import time
from collections import Counter

import httpx
from postgrest.exceptions import APIError
from supabase import create_client

from app.config import settings
from app.services.reviews.corpus import product_from_meta, review_from_record

BASE = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main"
BATCH = 500

client = create_client(settings.supabase_url, settings.supabase_service_key)
skipped = 0


def stream_records(url: str, attempts: int = 6):
    """Yield (record, bytes_read) from a remote .jsonl without caching to disk.

    A dropped connection part-way through a multi-gigabyte stream resumes with a
    Range request instead of restarting. The first line after a resume is
    discarded because the offset can land mid-line.
    """
    read = 0
    for attempt in range(attempts):
        headers = {"Range": f"bytes={read}-"} if read else {}
        resuming = read > 0
        try:
            with httpx.stream(
                "GET", url, headers=headers, follow_redirects=True, timeout=60
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    read += len(line) + 1
                    if resuming:
                        resuming = False
                        continue
                    if line:
                        yield json.loads(line), read
            return
        except httpx.HTTPError as error:
            if attempt == attempts - 1:
                raise
            print(f"\n  stream dropped at {read / 1e9:.2f} GB ({error}); resuming", flush=True)
            time.sleep(2**attempt)


def collect_products(category: str, limit: int) -> dict[str, dict]:
    """Scan metadata until `limit` in-tier, identifiable products are found."""
    url = f"{BASE}/raw/meta_categories/meta_{category}.jsonl"
    products: dict[str, dict] = {}
    for record, read in stream_records(url):
        product = product_from_meta(record)
        if product is not None:
            products[product["parent_asin"]] = product
            if len(products) % 1000 == 0:
                print(
                    f"  {len(products)}/{limit} products  ({read / 1e6:.0f} MB read)",
                    end="\r",
                    flush=True,
                )
            if len(products) >= limit:
                break
    print(f"  {len(products)} products  ({read / 1e6:.0f} MB read)" + " " * 20)
    return products


def collect_reviews(category: str, wanted: set[str], max_bytes: int, per_product: int) -> Counter:
    """Stream a review prefix, inserting matches in batches. Returns per-asin counts."""
    url = f"{BASE}/raw/review_categories/{category}.jsonl"
    counts: Counter = Counter()
    batch: list[dict] = []
    # The corpus repeats some (asin, user_id) pairs, and Postgres rejects an
    # upsert that touches the same conflict key twice in one statement.
    seen: set[tuple[str, str]] = set()
    kept = 0

    for record, read in stream_records(url):
        if read > max_bytes:
            break
        if record.get("parent_asin") not in wanted:
            continue
        if counts[record["parent_asin"]] >= per_product:
            continue

        review = review_from_record(record)
        if review is None:
            continue

        key = (review["asin"], review["user_id"])
        if key in seen:
            continue
        seen.add(key)

        counts[review["parent_asin"]] += 1
        batch.append(review)
        kept += 1
        if len(batch) >= BATCH:
            insert_reviews(batch)
            batch.clear()
            print(
                f"  {kept} reviews across {len(counts)} products"
                f"  ({read / 1e9:.2f}/{max_bytes / 1e9:.1f} GB)",
                end="\r",
                flush=True,
            )

    if batch:
        insert_reviews(batch)
    print(f"  {kept} reviews across {len(counts)} products" + " " * 30)
    return counts


def call(fn, attempts: int = 5):
    """Run a Supabase call, retrying transient network failures with backoff."""
    for attempt in range(attempts):
        try:
            return fn()
        except httpx.HTTPError:
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)


def insert_reviews(rows: list[dict]) -> None:
    """Insert a batch, falling back to row-at-a-time if the batch is rejected.

    Postgres rejects the whole statement when any single row is bad, and this
    corpus has enough surprises in it that losing a 5 GB run to one row is not
    an acceptable trade. Rows that still fail alone are counted and skipped.
    """
    global skipped
    try:
        call(lambda: client.table("reviews").upsert(rows, on_conflict="asin,user_id").execute())
    except APIError:
        for row in rows:
            try:
                call(
                    lambda: client.table("reviews")
                    .upsert([row], on_conflict="asin,user_id")
                    .execute()
                )
            except APIError:
                skipped += 1


def insert_products(rows: list[dict]) -> None:
    for start in range(0, len(rows), BATCH):
        chunk = rows[start : start + BATCH]
        call(lambda: client.table("products").upsert(chunk).execute())



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="Electronics", help="corpus category file")
    parser.add_argument("--max-products", type=int, default=20_000)
    parser.add_argument("--max-review-gb", type=float, default=5.0)
    parser.add_argument("--reviews-per-product", type=int, default=50)
    args = parser.parse_args()

    print(f"Scanning {args.category} metadata for in-tier products...")
    products = collect_products(args.category, args.max_products)

    print(f"Inserting {len(products)} candidate products...")
    insert_products(list(products.values()))

    print(f"Streaming up to {args.max_review_gb} GB of reviews...")
    counts = collect_reviews(
        args.category,
        set(products),
        int(args.max_review_gb * 1e9),
        args.reviews_per_product,
    )

    print(f"\nDone. {sum(counts.values())} reviews across {len(counts)} products.")
    if skipped:
        print(f"{skipped} reviews were rejected by Postgres and skipped.")
    print("Run data/seed/prune.sql once the ingest is complete to drop thin products.")
    if kept:
        top = counts.most_common(3)
        print(f"Best covered: {', '.join(f'{a} ({n})' for a, n in top)}")


if __name__ == "__main__":
    main()
