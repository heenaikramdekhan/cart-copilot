"""Agent 6 tests. The agent only repeats store-reported discounts, so the tests
pin exactly that: reported discounts surface, absent ones stay absent.
"""

from decimal import Decimal

from app.agents.deal_coupon import find_deals
from app.services.stores.models import Listing


def _listing(**overrides) -> Listing:
    base = dict(
        store="ebay",
        store_item_id="v1|1|0",
        title="Logitech MX Master 3S",
        price=Decimal("79.99"),
        currency="USD",
        url="https://www.ebay.com/itm/1",
    )
    return Listing(**{**base, **overrides})


def test_markdown_carries_the_stores_own_numbers():
    deals = find_deals([_listing(original_price=Decimal("99.99"), discount_percent=20)])

    assert len(deals) == 1
    assert deals[0].kind == "markdown"
    assert deals[0].store_item_id == "v1|1|0"
    assert deals[0].original_price == Decimal("99.99")
    assert deals[0].discount_percent == 20


def test_coupon_availability_is_its_own_deal():
    deals = find_deals([_listing(has_coupon=True)])

    assert [d.kind for d in deals] == ["coupon_available"]


def test_one_listing_can_yield_both():
    deals = find_deals(
        [_listing(original_price=Decimal("99.99"), discount_percent=20, has_coupon=True)]
    )

    assert [d.kind for d in deals] == ["markdown", "coupon_available"]


def test_absent_discount_is_not_a_deal():
    """No markdown, no coupon on the listing means no deal invented for it."""
    assert find_deals([_listing()]) == []
