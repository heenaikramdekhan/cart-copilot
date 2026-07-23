"""Catalog-mode mapping. The Supabase query is not exercised here — only that a
product row becomes a listing carrying the snapshot price and a real product
URL, marked as the catalog source so the UI can label it.
"""

from decimal import Decimal

from app.services.stores import catalog


def test_row_maps_to_a_catalog_listing():
    listing = catalog._listing(
        {
            "parent_asin": "B0BS9SB6XM",
            "title": "Logitech MX Master 3S",
            "brand": "Logitech",
            "model_number": "910-006556",
            "price": 98.4,
        }
    )

    assert listing.store == "catalog"
    assert listing.store_item_id == "B0BS9SB6XM"
    assert listing.price == Decimal("98.4")
    assert listing.mpn == "910-006556"
    assert listing.brand == "Logitech"
    assert listing.url == "https://www.amazon.com/dp/B0BS9SB6XM"
