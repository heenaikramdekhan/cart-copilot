"""Parse Amazon Reviews 2023 records into products/reviews rows.

Both parsers return None when a record cannot be used, so the caller filters on
one condition rather than duplicating validity rules.
"""

import re
from datetime import datetime, timezone

# Null bytes and unpaired surrogates: legal in a Python str, rejected by Postgres.
_UNSTORABLE = re.compile("[\x00\ud800-\udfff]")

# Locked tier categories, keyed by the corpus `categories` breadcrumb at depth 1.
# Tier 2 and 3 slugs get added here when those ingests run.
TIER_CATEGORIES = {
    "Computers & Accessories": "pc-peripherals",
}


def _clean(value: object) -> str | None:
    """Trim a corpus string field; empty and non-string values become None.

    Real review text contains null bytes and lone surrogates, neither of which
    Postgres `text` can store. They are stripped rather than escaped — they
    carry no meaning, and one of them rejects the whole insert batch.
    """
    if not isinstance(value, str):
        return None
    cleaned = _UNSTORABLE.sub("", value)
    return cleaned.strip() or None


def _model_number(value: object) -> str | None:
    """Reject free text sitting in the model number field.

    Real entries look like 'WD3200LPVT' or 'AF 24/1.8 FE'; the field also
    collects descriptions such as 'Abstract Leaves' and 'laptop backpack'. A
    model number that never matches an eBay MPN is worse than no model number,
    because it looks joinable.
    """
    model = _clean(value)
    if model is None:
        return None
    if len(model) > 40 or len(model.split()) > 3:
        return None
    if not any(char.isdigit() for char in model):
        return None
    return model


def _first_upc(value: object) -> str | None:
    """Corpus UPC fields sometimes list several codes; keep the first."""
    upc = _clean(value)
    if upc is None:
        return None
    return upc.split()[0]


def tier_slug(meta: dict) -> str | None:
    """The locked tier this item belongs to, or None if it is out of scope."""
    categories = meta.get("categories") or []
    if len(categories) < 2:
        return None
    return TIER_CATEGORIES.get(categories[1])


def product_from_meta(meta: dict) -> dict | None:
    """None when the item is out of scope or carries nothing to join on."""
    category = tier_slug(meta)
    if category is None:
        return None

    details = meta.get("details") or {}
    model_number = _model_number(details.get("Item model number"))
    upc = _first_upc(details.get("UPC"))
    if model_number is None and upc is None:
        return None

    title = _clean(meta.get("title"))
    if title is None:
        return None

    return {
        "parent_asin": meta["parent_asin"],
        "title": title,
        "brand": _clean(meta.get("store")),
        "model_number": model_number,
        "upc": upc,
        "category": category,
        "average_rating": meta.get("average_rating"),
        "rating_number": meta.get("rating_number"),
    }


def review_from_record(record: dict) -> dict | None:
    """None when the review has no body text to summarize."""
    body = _clean(record.get("text"))
    if body is None:
        return None

    return {
        "parent_asin": record["parent_asin"],
        "asin": record["asin"],
        "user_id": record["user_id"],
        "rating": int(record["rating"]),
        "title": _clean(record.get("title")),
        "body": body,
        "helpful_vote": record.get("helpful_vote") or 0,
        "verified_purchase": bool(record.get("verified_purchase")),
        # Corpus timestamps are epoch milliseconds.
        "reviewed_at": datetime.fromtimestamp(
            record["timestamp"] / 1000, tz=timezone.utc
        ).isoformat(),
    }
