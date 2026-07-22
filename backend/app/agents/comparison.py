"""Agent 3 — rank candidate listings against the user's requirements.

Deterministic by design: no LLM. Ranking a shopping list is arithmetic and
string matching, and a model would only make the result harder to explain and
harder to test.

The ordering rule, most significant first:

1. how many must-haves the listing satisfies
2. how many nice-to-haves it satisfies
3. condition (new beats refurbished beats used)
4. cheapest total cost

Anything over budget is dropped outright rather than ranked low — showing a
user something they said they cannot afford is not a ranking problem.
"""

import re
from decimal import Decimal

from app.graph.state import Requirements
from app.services.stores.models import Listing

# Words that carry no matching signal in a requirement like "at least 16GB RAM".
FILLER = {
    "a", "an", "and", "at", "for", "in", "least", "must", "of", "or", "the",
    "with", "have", "has", "support", "supports", "good", "some",
}

CONDITION_RANK = {"new": 2, "open box": 1, "refurbished": 1, "seller refurbished": 1}


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower())]


def _listing_tokens(listing: Listing) -> set[str]:
    """Everything a listing says about itself, as matchable tokens.

    Adjacent words are also joined so a requirement written "16GB" matches a
    listing that spells it "16 GB".
    """
    text = " ".join([listing.title, *listing.aspects.keys(), *listing.aspects.values()])
    words = _words(text)
    return set(words) | {a + b for a, b in zip(words, words[1:])}


def _satisfies(requirement: str, tokens: set[str]) -> bool:
    needed = {w for w in _words(requirement) if w not in FILLER}
    return bool(needed) and needed <= tokens


def _cost(listing: Listing) -> Decimal:
    """Total cost, falling back to price when shipping is unknown.

    Unknown shipping is not free shipping; it just cannot be ranked on.
    """
    return listing.total_cost if listing.total_cost is not None else listing.price


def _condition_rank(listing: Listing) -> int:
    if listing.condition is None:
        return 0
    return CONDITION_RANK.get(listing.condition.lower(), 0)


def rank(listings: list[Listing], requirements: Requirements, limit: int = 5) -> list[Listing]:
    """Return the best `limit` listings, best first."""
    affordable = [
        listing
        for listing in listings
        if requirements.budget is None or _cost(listing) <= Decimal(str(requirements.budget))
    ]

    def key(listing: Listing) -> tuple:
        tokens = _listing_tokens(listing)
        return (
            sum(_satisfies(r, tokens) for r in requirements.must_have),
            sum(_satisfies(r, tokens) for r in requirements.nice_to_have),
            _condition_rank(listing),
            -_cost(listing),
        )

    return sorted(affordable, key=key, reverse=True)[:limit]
