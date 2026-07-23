"""Chat route — understand the request, then search and rank against it.

Runs Agent 1 (Requirement Analyzer) → Agent 2 (Product Search) → Agent 3
(Comparison). Product Search needs eBay credentials; without them the route
returns the parsed requirements and says the store is unavailable rather than
an empty result that would read as "nothing found". Review summaries (Agent 4)
join the response once that agent is wired.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.requirement_analyzer import analyze
from app.graph.discovery import graph as discovery_graph
from app.graph.state import Requirements
from app.services import sessions
from app.services.stores import ebay_client
from app.services.stores.models import Listing

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    requirements: Requirements
    ranked_products: list[Listing]
    # Set while product search is unavailable, so the UI can say why the list
    # is empty instead of showing "no results found", which would be untrue.
    unavailable: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = sessions.get(request.session_id)
    state.user_query = request.message

    # Without a store to search, only Agent 1 can run. Report why rather than
    # returning an empty list that would read as "nothing found".
    if not ebay_client.configured:
        state.requirements = analyze(request.message)
        return ChatResponse(
            requirements=state.requirements,
            ranked_products=[],
            unavailable="eBay credentials are not configured yet, so no listings were fetched.",
        )

    result = discovery_graph.invoke(state)
    state.requirements = result["requirements"]
    state.search_results = result["search_results"]
    state.ranked_products = result["ranked_products"]
    return ChatResponse(
        requirements=state.requirements,
        ranked_products=state.ranked_products,
        unavailable=None if state.ranked_products else "No listings matched your requirements.",
    )
