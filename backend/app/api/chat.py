"""Chat route — understand the request, then search and rank against it.

Runs the discovery graph: Agent 1 (Requirement Analyzer) → Agent 2 (Product
Search) → Agent 3 (Comparison). Agent 2 searches eBay when its key is
configured and falls back to catalog mode otherwise, so the route always has
real products to rank. Review summaries (Agent 4) are fetched per product,
lazily, behind /api/reviews.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.discovery import graph as discovery_graph
from app.graph.state import Requirements
from app.services import sessions
from app.services.stores.models import Listing

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    requirements: Requirements
    ranked_products: list[Listing]
    # Set when the search returned nothing, so the UI can say so plainly.
    unavailable: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = sessions.get(request.session_id)
    state.user_query = request.message

    result = discovery_graph.invoke(state)
    state.requirements = result["requirements"]
    state.search_results = result["search_results"]
    state.ranked_products = result["ranked_products"]
    return ChatResponse(
        requirements=state.requirements,
        ranked_products=state.ranked_products,
        unavailable=None if state.ranked_products else "No listings matched your requirements.",
    )
