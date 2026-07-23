from decimal import Decimal

from app.graph.state import AgentState, CartFlag, CartItem, Requirements, ReviewSummary
from app.services.stores.models import Listing

LISTING = Listing(
    store="ebay",
    store_item_id="v1|254582474636|0",
    title="Logitech MX Master 3S",
    price=Decimal("79.99"),
    currency="USD",
    url="https://www.ebay.com/itm/254582474636",
)


def test_new_state_has_empty_collections_not_none():
    """Downstream agents iterate these before upstream agents have run."""
    state = AgentState(user_query="wireless mouse under $100")

    assert state.requirements is None
    assert state.search_results == []
    assert state.review_summaries == {}
    assert state.cart_flags == []


def test_agents_write_only_their_own_sections():
    state = AgentState(user_query="wireless mouse under $100")

    state.requirements = Requirements(budget=Decimal("100"), must_have=["wireless"])
    state.search_results = [LISTING]
    state.review_summaries[LISTING.store_item_id] = ReviewSummary(
        pros=["scroll wheel"], cons=["price"], based_on=42, corpus_through="2023-09"
    )
    state.cart = [CartItem(listing=LISTING)]
    state.cart_flags = [CartFlag(kind="cheaper_elsewhere", message="...", saves=Decimal("12"))]

    assert state.user_query == "wireless mouse under $100"
    assert state.requirements.budget == Decimal("100")
    assert state.review_summaries[LISTING.store_item_id].based_on == 42
    assert state.cart[0].quantity == 1


def test_review_summary_requires_provenance():
    """A summary must always say how many reviews and how old they are."""
    summary = ReviewSummary(pros=[], cons=[], based_on=3, corpus_through="2023-09")

    assert summary.based_on == 3
    assert summary.corpus_through == "2023-09"
