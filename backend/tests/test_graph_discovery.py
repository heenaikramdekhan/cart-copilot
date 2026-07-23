"""Discovery graph wiring. The agents are stubbed so this checks the pipeline
order and data flow — Agent 1's output reaches Agent 2, whose output reaches
Agent 3 — without any network or LLM call.
"""

from decimal import Decimal

from app.graph import discovery
from app.graph.state import AgentState, Requirements
from app.services.stores.models import Listing


def _listing(item_id: str) -> Listing:
    return Listing(
        store="ebay",
        store_item_id=item_id,
        title="Mouse",
        price=Decimal("10"),
        currency="USD",
        url="https://www.ebay.com/itm/" + item_id,
    )


def test_pipeline_flows_analyze_to_search_to_compare(monkeypatch):
    reqs = Requirements(category="mouse")
    found = [_listing("1"), _listing("2")]

    monkeypatch.setattr(discovery.requirement_analyzer, "analyze", lambda query: reqs)
    monkeypatch.setattr(discovery.product_search, "search", lambda r: found)
    # rank receives search's output and the requirements; reverse to prove the
    # ordering is the ranker's, not the search order.
    monkeypatch.setattr(discovery.comparison, "rank", lambda listings, r: list(reversed(listings)))

    result = discovery.graph.invoke(AgentState(user_query="a mouse"))

    assert result["requirements"] == reqs
    assert [l.store_item_id for l in result["search_results"]] == ["1", "2"]
    assert [l.store_item_id for l in result["ranked_products"]] == ["2", "1"]
