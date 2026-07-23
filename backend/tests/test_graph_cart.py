"""Cart graph wiring. The agents are stubbed so this checks that both branches
run and each writes its own state — Cart Optimization (5) and Deal & Coupon (6)
are parallel and independent.
"""

from decimal import Decimal

from app.graph import cart
from app.graph.state import AgentState, CartFlag, CartItem, Deal
from app.services.stores.models import Listing


def _item(item_id: str) -> CartItem:
    return CartItem(
        listing=Listing(
            store="ebay",
            store_item_id=item_id,
            title="Mouse",
            price=Decimal("10"),
            currency="USD",
            url="https://www.ebay.com/itm/" + item_id,
        )
    )


def test_both_branches_run_and_write_their_own_state(monkeypatch):
    flag = CartFlag(kind="duplicate", message="in your cart twice")
    deal = Deal(store_item_id="1", kind="markdown")

    monkeypatch.setattr(cart.cart_optimization, "check", lambda cart_items, alts: [flag])
    monkeypatch.setattr(cart.cart_optimization, "narrate", lambda flags: "here is the advice")
    monkeypatch.setattr(cart.deal_coupon, "find_deals", lambda listings: [deal])

    result = cart.graph.invoke(AgentState(user_query="", cart=[_item("1")]))

    assert result["cart_flags"] == [flag]
    assert result["cart_advice"] == "here is the advice"
    assert result["deals"] == [deal]
