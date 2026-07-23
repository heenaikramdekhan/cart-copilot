"""Agent 6 — Deal & Coupon.

Surfaces the discounts a store already reports on a listing: a markdown against
an earlier price, and whether a coupon is available. Deterministic by design —
no LLM, and nothing inferred. Real retailers do not publish their coupon rules,
so this agent never matches against invented ones; it only repeats what the
store's own response carried.
"""

from app.graph.state import Deal
from app.services.stores.models import Listing


def find_deals(listings: list[Listing]) -> list[Deal]:
    """Every store-reported markdown and coupon across the given listings.

    A listing can yield both: a markdown and, separately, an available coupon.
    A listing carrying neither yields nothing — an absent discount is not a
    zero discount.
    """
    deals = []
    for listing in listings:
        if listing.original_price is not None or listing.discount_percent is not None:
            deals.append(
                Deal(
                    store_item_id=listing.store_item_id,
                    kind="markdown",
                    original_price=listing.original_price,
                    discount_percent=listing.discount_percent,
                )
            )
        if listing.has_coupon:
            deals.append(
                Deal(store_item_id=listing.store_item_id, kind="coupon_available")
            )
    return deals
