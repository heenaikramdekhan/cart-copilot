from decimal import Decimal

from app.agents.comparison import rank
from app.graph.state import Requirements
from app.services.stores.models import Listing


def listing(item_id, title, price, shipping=None, condition="New", aspects=None):
    return Listing(
        store="ebay",
        store_item_id=item_id,
        title=title,
        price=Decimal(price),
        currency="USD",
        url=f"https://www.ebay.com/itm/{item_id}",
        shipping_cost=Decimal(shipping) if shipping else None,
        condition=condition,
        aspects=aspects or {},
    )


def test_must_haves_outrank_price():
    cheap = listing("1", "Gaming Laptop 8GB RAM", "500")
    fitting = listing("2", "Gaming Laptop 16GB RAM", "800")

    ranked = rank([cheap, fitting], Requirements(must_have=["16GB RAM"]))

    assert [x.store_item_id for x in ranked] == ["2", "1"]


def test_spelling_of_specs_does_not_decide_the_match():
    """A listing writing '16 GB' must satisfy a requirement written '16GB'."""
    spaced = listing("1", "Laptop", "800", aspects={"RAM": "16 GB"})

    ranked = rank([spaced], Requirements(must_have=["16GB RAM"]))

    assert ranked == [spaced]


def test_over_budget_listings_are_dropped_not_demoted():
    over = listing("1", "Laptop 16GB RAM", "950")
    under = listing("2", "Laptop 8GB RAM", "600")

    ranked = rank([over, under], Requirements(budget=900, must_have=["16GB RAM"]))

    assert [x.store_item_id for x in ranked] == ["2"]


def test_budget_counts_shipping():
    """Cheap item plus heavy shipping can still exceed the budget."""
    sneaky = listing("1", "Monitor", "95", shipping="20")

    assert rank([sneaky], Requirements(budget=100)) == []


def test_unknown_shipping_does_not_become_free_shipping():
    """It ranks on price alone rather than being treated as costing nothing."""
    unknown = listing("1", "Monitor", "95", shipping=None)

    assert rank([unknown], Requirements(budget=100)) == [unknown]


def test_condition_breaks_ties_before_price():
    used = listing("1", "Keyboard", "40", condition="Used")
    refurb = listing("2", "Keyboard", "45", condition="Refurbished")
    new = listing("3", "Keyboard", "50", condition="New")

    ranked = rank([used, refurb, new], Requirements())

    assert [x.store_item_id for x in ranked] == ["3", "2", "1"]


def test_nice_to_haves_only_separate_equal_must_have_matches():
    plain = listing("1", "Monitor 27 inch", "300")
    better = listing("2", "Monitor 27 inch 1440p", "320")

    ranked = rank([plain, better], Requirements(must_have=["27 inch"], nice_to_have=["1440p"]))

    assert [x.store_item_id for x in ranked] == ["2", "1"]


def test_returns_at_most_the_limit():
    many = [listing(str(i), f"Mouse {i}", str(20 + i)) for i in range(9)]

    assert len(rank(many, Requirements())) == 5
