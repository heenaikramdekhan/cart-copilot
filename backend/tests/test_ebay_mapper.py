"""Mapper tests for the eBay Browse API.

The fixtures below follow eBay's documented ItemSummary / Item field structure.
They must be re-checked against a real API response once credentials exist —
doc-derived fixtures prove the mapping logic, not the field names.
"""

from decimal import Decimal

from app.services.stores.ebay import enrich, listing_from_summary

SUMMARY = {
    "itemId": "v1|254582474636|0",
    "title": "Logitech MX Master 3S Wireless Mouse",
    "price": {"value": "79.99", "currency": "USD"},
    "itemWebUrl": "https://www.ebay.com/itm/254582474636",
    "condition": "New",
    "seller": {"username": "techdeals", "feedbackPercentage": "99.3"},
    "image": {"imageUrl": "https://i.ebayimg.com/images/g/abc/s-l225.jpg"},
    "shippingOptions": [
        {"shippingCostType": "FIXED", "shippingCost": {"value": "4.95", "currency": "USD"}}
    ],
}


def test_maps_core_offer_fields():
    listing = listing_from_summary(SUMMARY)

    assert listing.store == "ebay"
    assert listing.store_item_id == "v1|254582474636|0"
    assert listing.price == Decimal("79.99")
    assert listing.currency == "USD"
    assert listing.shipping_cost == Decimal("4.95")
    assert listing.seller == "techdeals"
    assert listing.total_cost == Decimal("84.94")


def test_search_results_carry_no_product_identity():
    """ItemSummary has no gtin/mpn/brand — the join needs the detail call."""
    listing = listing_from_summary(SUMMARY)

    assert listing.gtin is None
    assert listing.mpn is None
    assert listing.brand is None


def test_unknown_shipping_stays_unknown():
    """No shipping data must not become free shipping."""
    summary = {k: v for k, v in SUMMARY.items() if k != "shippingOptions"}

    listing = listing_from_summary(summary)

    assert listing.shipping_cost is None
    assert listing.total_cost is None


def test_enrich_adds_product_identity():
    listing = listing_from_summary(SUMMARY)

    enriched = enrich(
        listing,
        {"gtin": "0097855172303", "mpn": "910-006556", "brand": "Logitech"},
    )

    assert enriched.gtin == "0097855172303"
    assert enriched.mpn == "910-006556"
    assert enriched.brand == "Logitech"
    assert enriched.price == listing.price
