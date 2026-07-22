"""Chat route — understand what the shopper is asking for.

Today this runs Agent 1 and stops. Search, comparison and review summaries join
the response once Agent 2 can reach a live store; the response shape already
carries them so the frontend does not change when it does.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.requirement_analyzer import analyze
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
    # Set while product search is unavailable, so the UI can say why the list
    # is empty instead of showing "no results found", which would be untrue.
    unavailable: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = sessions.get(request.session_id)
    state.user_query = request.message
    state.requirements = analyze(request.message)

    return ChatResponse(
        requirements=state.requirements,
        ranked_products=state.ranked_products,
        unavailable="Product search is not connected yet, so no listings were fetched.",
    )
