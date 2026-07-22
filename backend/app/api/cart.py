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

from app.agents.cart_optimization import check, narrate
from app.graph.state import CartFlag, CartItem
from app.services import sessions
from app.services.stores.models import Listing

router = APIRouter(prefix="/api/cart", tags=["cart"])


class AddItemRequest(BaseModel):
    listing: Listing
    quantity: int = 1


class CartResponse(BaseModel):
    items: list[CartItem]
    flags: list[CartFlag]
    advice: str | None = None


def _respond(session_id: str, recompute_advice: bool) -> CartResponse:
    state = sessions.get(session_id)
    state.cart_flags = check(state.cart)
    if recompute_advice:
        state.cart_advice = narrate(state.cart_flags)
    return CartResponse(items=state.cart, flags=state.cart_flags, advice=state.cart_advice)


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
