"""Agent 2 tests. The store client is stubbed so these check query building and
pass-through only — the live call is covered in test_ebay_client.
"""

from decimal import Decimal

from app.agents import product_search
from app.graph.state import Requirements
from app.services.stores.models import Listing


def test_query_uses_category_and_must_haves():
    reqs = Requirements(
        category="laptop",
        must_have=["16GB RAM"],
        nice_to_have=["backlit keyboard"],
    )
    assert product_search._query(reqs) == "laptop 16GB RAM"


def test_empty_requirements_do_not_hit_the_store(monkeypatch):
    """No category and no must-haves means there is nothing to search for."""
    def fail(query):
        raise AssertionError("store should not be called")

    monkeypatch.setattr(product_search.ebay_client, "search", fail)
    assert product_search.search(Requirements()) == []


def test_search_passes_the_query_to_the_store(monkeypatch):
    captured = {}

    def fake(query):
        captured["q"] = query
        return [
            Listing(
                store="ebay",
                store_item_id="1",
                title="X",
                price=Decimal("10"),
                currency="USD",
                url="https://ebay.com/itm/1",
            )
        ]

    monkeypatch.setattr(product_search.ebay_client, "configured", True)
    monkeypatch.setattr(product_search.ebay_client, "search", fake)
    results = product_search.search(Requirements(category="mouse"))

    assert captured["q"] == "mouse"
    assert len(results) == 1


def test_falls_back_to_catalog_when_ebay_unconfigured(monkeypatch):
    captured = {}
    monkeypatch.setattr(product_search.ebay_client, "configured", False)
    monkeypatch.setattr(
        product_search.ebay_client,
        "search",
        lambda q: (_ for _ in ()).throw(AssertionError("eBay must not run when unconfigured")),
    )
    monkeypatch.setattr(
        product_search.catalog, "search", lambda reqs: captured.setdefault("reqs", reqs) or []
    )

    reqs = Requirements(category="mouse")
    product_search.search(reqs)

    assert captured["reqs"] is reqs
