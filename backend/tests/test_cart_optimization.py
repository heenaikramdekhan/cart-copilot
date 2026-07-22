from decimal import Decimal

from app.agents.cart_optimization import check
from app.graph.state import CartItem
from app.services.stores.models import Listing


def listing(item_id, title, price, shipping=None, seller="seller_a", mpn=None, gtin=None, brand="Logitech"):
    return Listing(
        store="ebay",
        store_item_id=item_id,
        title=title,
        price=Decimal(price),
        currency="USD",
        url=f"https://www.ebay.com/itm/{item_id}",
        shipping_cost=Decimal(shipping) if shipping else None,
        seller=seller,
        brand=brand,
        mpn=mpn,
        gtin=gtin,
    )


def cart(*listings):
    return [CartItem(listing=x) for x in listings]


def test_same_product_from_two_sellers_is_a_duplicate():
    a = listing("1", "MX Master 3S", "80", mpn="910-006556", seller="techdeals")
    b = listing("2", "MX Master 3S", "85", mpn="910-006556", seller="gadgetworld")

    flags = check(cart(a, b))

    assert [f.kind for f in flags] == ["duplicate"]
    assert flags[0].saves == Decimal("80")


def test_similar_titles_are_not_treated_as_the_same_product():
    """Different MPNs mean different products, however alike the titles read."""
    a = listing("1", "MX Master 3S Wireless Mouse", "80", mpn="910-006556")
    b = listing("2", "MX Master 3S Wireless Mouse", "85", mpn="910-006557")

    assert check(cart(a, b)) == []


def test_listings_without_identity_are_left_alone():
    """No GTIN and no MPN means nothing can be proved — say nothing."""
    a = listing("1", "Wireless Mouse", "80", mpn=None)
    b = listing("2", "Wireless Mouse", "85", mpn=None)

    assert check(cart(a, b)) == []


def test_cheaper_identical_listing_is_reported_with_the_saving():
    in_cart = listing("1", "MX Master 3S", "80", mpn="910-006556", seller="techdeals")
    elsewhere = listing("9", "MX Master 3S", "62", mpn="910-006556", seller="bargainbin")

    flags = check(cart(in_cart), alternatives=[elsewhere])

    assert flags[0].kind == "cheaper_elsewhere"
    assert flags[0].saves == Decimal("18")


def test_cheaper_alternative_is_judged_on_total_cost_not_price():
    """A lower sticker price with heavy postage is not cheaper."""
    in_cart = listing("1", "MX Master 3S", "80", shipping="0", mpn="910-006556")
    fake_bargain = listing("9", "MX Master 3S", "70", shipping="25", mpn="910-006556")

    assert check(cart(in_cart), alternatives=[fake_bargain]) == []


def test_repeated_postage_to_one_seller_is_flagged():
    a = listing("1", "Keyboard", "60", shipping="5", seller="techdeals", mpn="K1")
    b = listing("2", "Mouse", "40", shipping="5", seller="techdeals", mpn="M1")
    c = listing("3", "Cable", "10", shipping="4", seller="techdeals", mpn="C1")

    flags = check(cart(a, b, c))

    assert flags[0].kind == "shipping_consolidation"
    assert flags[0].saves == Decimal("9")  # 5 + 5 + 4, minus the one shipment you still pay


def test_postage_to_different_sellers_cannot_be_combined():
    a = listing("1", "Keyboard", "60", shipping="5", seller="techdeals", mpn="K1")
    b = listing("2", "Mouse", "40", shipping="5", seller="gadgetworld", mpn="M1")

    assert check(cart(a, b)) == []


def test_flags_are_ordered_by_how_much_they_save():
    dup_a = listing("1", "MX Master 3S", "80", shipping="5", seller="techdeals", mpn="910-006556")
    dup_b = listing("2", "MX Master 3S", "80", shipping="5", seller="techdeals", mpn="910-006556")

    flags = check(cart(dup_a, dup_b))

    assert [f.kind for f in flags] == ["duplicate", "shipping_consolidation"]
    assert flags[0].saves > flags[1].saves
