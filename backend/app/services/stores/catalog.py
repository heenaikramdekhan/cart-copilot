"""Catalog-mode product source, backed by the ingested review corpus.

A stand-in for a live store while no store API key is configured. It returns
the real products already in Supabase, priced from the corpus's Sept 2023
snapshot. Listings carry store='catalog' so the UI can label the pricing as a
snapshot rather than live, and so a live store transparently replaces it once
its key lands.

Only priced products are returned: a listing with no price cannot be ranked,
carted, or checked against a budget. Because these rows are the same ones the
review corpus is keyed on, every catalog listing already has reviews to match.
"""

from decimal import Decimal

from supabase import create_client

from app.config import settings
from app.graph.state import Requirements
from app.services.stores.models import Listing

STORE = "catalog"

_client = create_client(settings.supabase_url, settings.supabase_service_key)


def _listing(row: dict) -> Listing:
    return Listing(
        store=STORE,
        store_item_id=row["parent_asin"],
        title=row["title"],
        price=Decimal(str(row["price"])),
        currency="USD",
        # The real Amazon product page for this identity.
        url=f"https://www.amazon.com/dp/{row['parent_asin']}",
        brand=row["brand"],
        mpn=row["model_number"],
        rating=row["average_rating"],
        rating_count=row["rating_number"],
    )


def search(requirements: Requirements, limit: int = 20) -> list[Listing]:
    """Priced catalog products whose title matches the requested category."""
    query = (
        _client.table("products")
        .select("parent_asin,title,brand,model_number,price,average_rating,rating_number")
        .not_.is_("price", "null")
    )
    if requirements.category:
        query = query.ilike("title", f"%{requirements.category}%")
    rows = query.limit(limit).execute().data
    return [_listing(row) for row in rows]
