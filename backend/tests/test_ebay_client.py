"""Client tests for the eBay Browse API, driven by a mock transport so no test
touches the network. Fixtures follow eBay's documented response structure and
must be re-checked against a real response once credentials exist.
"""

from decimal import Decimal

import httpx
import pytest

from app.services.stores import ebay_client

TOKEN = {"access_token": "tok-abc", "expires_in": 7200}

SEARCH = {
    "itemSummaries": [
        {
            "itemId": "v1|111|0",
            "title": "Logitech MX Master 3S",
            "price": {"value": "79.99", "currency": "USD"},
            "itemWebUrl": "https://www.ebay.com/itm/111",
        }
    ]
}

ITEMS = {
    "items": [
        {
            "itemId": "v1|111|0",
            "mpn": "910-006556",
            "brand": "Logitech",
            "localizedAspects": [{"name": "Connectivity", "value": "Wireless"}],
        }
    ]
}


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/oauth2/token"):
        return httpx.Response(200, json=TOKEN)
    if "item_summary/search" in request.url.path:
        return httpx.Response(200, json=SEARCH)
    if request.url.path.endswith("/buy/browse/v1/item/"):
        return httpx.Response(200, json=ITEMS)
    return httpx.Response(404)


@pytest.fixture
def mock_ebay(monkeypatch):
    client = httpx.Client(
        base_url="https://api.ebay.com", transport=httpx.MockTransport(_handler)
    )
    monkeypatch.setattr(ebay_client, "_http", client)
    monkeypatch.setattr(ebay_client, "_token", None)
    return client


def test_search_returns_identity_enriched_listings(mock_ebay):
    """The detail call's identity and specs are joined onto the search offer."""
    listings = ebay_client.search("wireless mouse")

    assert len(listings) == 1
    listing = listings[0]
    assert listing.store == "ebay"
    assert listing.price == Decimal("79.99")
    assert listing.mpn == "910-006556"
    assert listing.brand == "Logitech"
    assert listing.aspects == {"Connectivity": "Wireless"}


def test_empty_search_skips_the_detail_call(mock_ebay, monkeypatch):
    monkeypatch.setitem(SEARCH, "itemSummaries", [])
    assert ebay_client.search("nothing here") == []
