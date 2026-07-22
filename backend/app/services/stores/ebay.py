"""Map eBay Browse API responses onto the normalized Listing shape.

Two calls are needed per user query: item_summary/search returns offers but no
product identifiers, and item/?item_ids= returns gtin/mpn/brand in bulk. The
mappers are kept separate so each is testable without the network.
"""

from decimal import Decimal

from app.services.stores.models import Listing

STORE = "ebay"


def _amount(value: dict | None) -> Decimal | None:
    """Pull a Decimal out of an eBay amount object, or None if absent."""
    if not value or "value" not in value:
        return None
    return Decimal(str(value["value"]))


def _shipping_cost(summary: dict) -> Decimal | None:
    """Cost of the first shipping option, or None if eBay reported none."""
    options = summary.get("shippingOptions") or []
    if not options:
        return None
    return _amount(options[0].get("shippingCost"))


def listing_from_summary(summary: dict) -> Listing:
    """Map one itemSummaries entry. Carries no product identity — see enrich()."""
    price = summary["price"]
    return Listing(
        store=STORE,
        store_item_id=summary["itemId"],
        title=summary["title"],
        price=Decimal(str(price["value"])),
        currency=price["currency"],
        url=summary["itemWebUrl"],
        shipping_cost=_shipping_cost(summary),
        condition=summary.get("condition"),
        seller=(summary.get("seller") or {}).get("username"),
        image_url=(summary.get("image") or {}).get("imageUrl"),
    )


def enrich(listing: Listing, item: dict) -> Listing:
    """Add gtin/mpn/brand from a getItems detail response."""
    return listing.model_copy(
        update={
            "gtin": item.get("gtin"),
            "mpn": item.get("mpn"),
            "brand": item.get("brand"),
        }
    )
