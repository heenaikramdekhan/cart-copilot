"""Live eBay Browse API client.

Kept apart from ebay.py's mappers so the mapping stays testable without the
network and this stays testable with a mock transport. Two calls make one
search: item_summary/search returns priced offers with no product identity,
and item/?item_ids= returns gtin/mpn/brand/aspects in bulk. The two are joined
back together by itemId.

Credentials are optional so the app boots without them. When they are absent
`configured` is False and the search agent reports the store as unavailable
rather than fabricating results.
"""

import base64
import time

import httpx

from app.config import settings
from app.services.stores import ebay
from app.services.stores.models import Listing

_BASE = "https://api.ebay.com"
_SCOPE = "https://api.ebay.com/oauth/api_scope"
_MARKETPLACE = "EBAY_US"

configured = bool(settings.ebay_app_id and settings.ebay_cert_id)

_http: httpx.Client | None = None
_token: tuple[str, float] | None = None  # (access_token, monotonic expiry)


def _client() -> httpx.Client:
    global _http
    if _http is None:
        _http = httpx.Client(base_url=_BASE, timeout=15)
    return _http


def _access_token() -> str:
    """A client-credentials token, cached until shortly before it expires."""
    global _token
    if _token is not None and _token[1] > time.monotonic():
        return _token[0]
    basic = base64.b64encode(
        f"{settings.ebay_app_id}:{settings.ebay_cert_id}".encode()
    ).decode()
    response = _client().post(
        "/identity/v1/oauth2/token",
        headers={"Authorization": f"Basic {basic}"},
        data={"grant_type": "client_credentials", "scope": _SCOPE},
    )
    response.raise_for_status()
    body = response.json()
    # Refresh a minute early so a token never expires mid-request.
    _token = (body["access_token"], time.monotonic() + body["expires_in"] - 60)
    return _token[0]


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_access_token()}",
        "X-EBAY-C-MARKETPLACE-ID": _MARKETPLACE,
    }


def search(query: str, limit: int = 20) -> list[Listing]:
    """Search eBay and return normalized, identity-enriched listings.

    `limit` stays at or below 20 because getItems accepts at most 20 item_ids
    in one call, and one search maps to one detail call by design.
    """
    summaries = _client().get(
        "/buy/browse/v1/item_summary/search",
        headers=_headers(),
        params={"q": query, "limit": limit},
    )
    summaries.raise_for_status()
    listings = [
        ebay.listing_from_summary(s)
        for s in summaries.json().get("itemSummaries", [])
    ]
    if not listings:
        return []

    details = _client().get(
        "/buy/browse/v1/item/",
        headers=_headers(),
        params={"item_ids": ",".join(l.store_item_id for l in listings)},
    )
    details.raise_for_status()
    items = {item["itemId"]: item for item in details.json().get("items", [])}
    return [
        ebay.enrich(l, items[l.store_item_id]) if l.store_item_id in items else l
        for l in listings
    ]
