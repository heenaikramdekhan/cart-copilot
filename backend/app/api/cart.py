"""Cart routes — add, remove, and reason over what the shopper has picked.

Cart CRUD is kept separate from chat because the two change for different
reasons: adding an item is a plain state change, while chat runs agents.

Rule checks run on every read because they are free and always current. The
written recommendation costs an LLM call, so it is regenerated only when the
cart actually changes and cached in between — the free tier allows five
requests a minute, and a cart is read far more often than it is edited.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents import cart_optimization, deal_coupon
from app.graph.cart import graph as cart_graph
from app.graph.state import CartFlag, CartItem, Deal
from app.services import sessions
from app.services.llm import LLMError
from app.services.stores.models import Listing

router = APIRouter(prefix="/api/cart", tags=["cart"])


class AddItemRequest(BaseModel):
    listing: Listing
    quantity: int = 1


class CartResponse(BaseModel):
    items: list[CartItem]
    flags: list[CartFlag]
    advice: str | None = None
    deals: list[Deal] = []


def _respond(session_id: str, recompute_advice: bool) -> CartResponse:
    state = sessions.get(session_id)
    if recompute_advice:
        # The cart changed: run the cart graph so Agents 5 and 6 recompute in
        # parallel, including the LLM-written advice.
        try:
            result = cart_graph.invoke(state)
            state.cart_flags = result["cart_flags"]
            state.cart_advice = result["cart_advice"]
            state.deals = result["deals"]
        except LLMError:
            # Only the written advice needs the AI. If it is rate limited, still
            # give the shopper their flags and deals rather than failing the add.
            state.cart_flags = cart_optimization.check(state.cart, state.search_results)
            state.deals = deal_coupon.find_deals([item.listing for item in state.cart])
            state.cart_advice = None
    else:
        # A plain read: refresh the free deterministic outputs and reuse the
        # cached advice, so a read never spends an LLM call.
        state.cart_flags = cart_optimization.check(state.cart, state.search_results)
        state.deals = deal_coupon.find_deals([item.listing for item in state.cart])
    return CartResponse(
        items=state.cart,
        flags=state.cart_flags,
        advice=state.cart_advice,
        deals=state.deals,
    )


@router.get("/{session_id}", response_model=CartResponse)
def read_cart(session_id: str) -> CartResponse:
    return _respond(session_id, recompute_advice=False)


@router.post("/{session_id}/items", response_model=CartResponse, status_code=201)
def add_item(session_id: str, request: AddItemRequest) -> CartResponse:
    state = sessions.get(session_id)
    state.cart.append(CartItem(listing=request.listing, quantity=request.quantity))
    return _respond(session_id, recompute_advice=True)


@router.delete("/{session_id}/items/{store_item_id}", response_model=CartResponse)
def remove_item(session_id: str, store_item_id: str) -> CartResponse:
    """Remove one line. Needed to act on a duplicate flag, not just read it."""
    state = sessions.get(session_id)
    remaining = [item for item in state.cart if item.listing.store_item_id != store_item_id]
    if len(remaining) == len(state.cart):
        raise HTTPException(status_code=404, detail=f"{store_item_id} is not in this cart")

    state.cart = remaining
    return _respond(session_id, recompute_advice=True)
