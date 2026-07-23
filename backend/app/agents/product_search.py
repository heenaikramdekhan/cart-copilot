"""Agent 2 — Product Search.

Turns the analyzed requirements into a live store query and returns normalized
candidate listings. Deterministic by design: no LLM. Fanning out to a store API
and normalizing the response is I/O and mapping, not reasoning.

eBay is the live source. Until its key is configured, the search falls back to
catalog mode — the ingested corpus priced from its Sept 2023 snapshot — so the
rest of the pipeline has real products to work on. The fallback disappears on
its own once eBay is configured. Best Buy is the planned second live leg.
"""

from app.graph.state import Requirements
from app.services.stores import catalog, ebay_client
from app.services.stores.models import Listing


def _query(requirements: Requirements) -> str:
    """Build a store query from the hard parts of the request.

    Category and must-haves are what the shopper stated outright, so they drive
    the search. Nice-to-haves are left for Comparison to rank on rather than
    narrowing the result set here.
    """
    parts = [requirements.category, *requirements.must_have]
    return " ".join(p for p in parts if p)


def search(requirements: Requirements) -> list[Listing]:
    query = _query(requirements)
    if not query:
        return []
    if ebay_client.configured:
        return ebay_client.search(query)
    return catalog.search(requirements)
