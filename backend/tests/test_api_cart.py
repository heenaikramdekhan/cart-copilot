"""Cart API tests.

`narrate` is stubbed out: it costs a rate-limited LLM call, and what these
tests are checking is the cart behaviour around it, not its wording.
"""

import pytest
from fastapi.testclient import TestClient

from app.agents import cart_optimization
from app.main import app
from app.services import sessions

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_session(monkeypatch):
    sessions.clear()
    # narrate runs inside the cart graph now; stub it where the graph looks it up.
    monkeypatch.setattr(cart_optimization, "narrate", lambda flags: f"advice for {len(flags)} flags")


def item(item_id, title="Logitech MX Master 3S", price="80", mpn="910-006556", shipping=None):
    return {
        "listing": {
            "store": "ebay",
            "store_item_id": item_id,
            "title": title,
            "price": price,
            "currency": "USD",
            "url": f"https://www.ebay.com/itm/{item_id}",
            "shipping_cost": shipping,
            "seller": "techdeals",
            "brand": "Logitech",
            "mpn": mpn,
        }
    }


def test_unknown_session_returns_an_empty_cart_not_an_error():
    r = client.get("/api/cart/never-seen")

    assert r.status_code == 200
    assert r.json() == {"items": [], "flags": [], "advice": None, "deals": []}


def test_adding_an_item_returns_the_updated_cart():
    r = client.post("/api/cart/s1/items", json=item("1"))

    assert r.status_code == 201
    assert len(r.json()["items"]) == 1


def test_adding_the_same_product_twice_raises_a_duplicate_flag():
    client.post("/api/cart/s1/items", json=item("1"))
    r = client.post("/api/cart/s1/items", json=item("2", price="84"))

    flags = r.json()["flags"]
    assert [f["kind"] for f in flags] == ["duplicate"]
    assert r.json()["advice"] == "advice for 1 flags"


def test_removing_the_duplicate_clears_the_flag():
    client.post("/api/cart/s1/items", json=item("1"))
    client.post("/api/cart/s1/items", json=item("2", price="84"))

    r = client.delete("/api/cart/s1/items/2")

    assert r.status_code == 200
    assert r.json()["flags"] == []
    assert len(r.json()["items"]) == 1


def test_removing_something_not_in_the_cart_is_a_404():
    client.post("/api/cart/s1/items", json=item("1"))

    assert client.delete("/api/cart/s1/items/nope").status_code == 404


def test_reading_the_cart_does_not_regenerate_the_advice():
    """The advice costs a rate-limited call; reads must reuse the cached one."""
    client.post("/api/cart/s1/items", json=item("1"))
    client.post("/api/cart/s1/items", json=item("2", price="84"))

    calls = []
    cart_optimization.narrate = lambda flags: calls.append(flags) or "regenerated"

    r = client.get("/api/cart/s1")

    assert calls == []
    assert r.json()["advice"] == "advice for 1 flags"


def test_sessions_do_not_leak_into_each_other():
    client.post("/api/cart/s1/items", json=item("1"))

    assert client.get("/api/cart/s2").json()["items"] == []
