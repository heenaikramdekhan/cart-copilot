"""Agent 5 — reason over the whole cart, not one item at a time.

This is the differentiator: an assistant that notices you are about to pay
twice for the same thing, or pay postage three times to one seller.

The rule checks live here and are deterministic — a saving either exists or it
does not, and a model guessing at arithmetic would make it unverifiable. The
natural-language recommendation built on top of these flags is the LLM half of
this agent and lives separately.

Items are matched by product identity (GTIN, or brand plus manufacturer part
number), never by title. Two listings with similar titles are routinely
different products, and telling someone to buy the cheaper one would be wrong.
"""

from decimal import Decimal

from google.genai import types

from app.graph.state import CartFlag, CartItem
from app.prompts.cart_optimization import SYSTEM
from app.services.llm import MODEL, client
from app.services.stores.models import Listing


def _identity(listing: Listing) -> tuple | None:
    """A key two listings share only if they are the same product."""
    if listing.gtin:
        return ("gtin", listing.gtin)
    if listing.brand and listing.mpn:
        return ("mpn", listing.brand.lower(), listing.mpn.lower())
    return None


def _duplicates(cart: list[CartItem]) -> list[CartFlag]:
    """The same product added twice as separate lines."""
    seen: dict[tuple, CartItem] = {}
    flags = []
    for item in cart:
        key = _identity(item.listing)
        if key is None:
            continue
        if key in seen:
            first = seen[key].listing
            here, there = (first.seller or first.store), (item.listing.seller or item.listing.store)
            where = f"twice from {here}" if here == there else f"from both {here} and {there}"
            flags.append(
                CartFlag(
                    kind="duplicate",
                    message=f"{item.listing.title} is in your cart {where}.",
                    saves=min(first.cost, item.listing.cost),
                )
            )
        else:
            seen[key] = item
    return flags


def _cheaper_elsewhere(cart: list[CartItem], alternatives: list[Listing]) -> list[CartFlag]:
    """The identical product offered for less by another seller."""
    flags = []
    for item in cart:
        key = _identity(item.listing)
        if key is None:
            continue
        cheaper = [
            other
            for other in alternatives
            if _identity(other) == key
            and other.store_item_id != item.listing.store_item_id
            and other.cost < item.listing.cost
        ]
        if not cheaper:
            continue
        best = min(cheaper, key=lambda listing: listing.cost)
        flags.append(
            CartFlag(
                kind="cheaper_elsewhere",
                message=(
                    f"The same {item.listing.title} is {best.cost} from "
                    f"{best.seller or best.store}, against {item.listing.cost} in your cart."
                ),
                saves=item.listing.cost - best.cost,
            )
        )
    return flags


def _split_shipping(cart: list[CartItem]) -> list[CartFlag]:
    """Postage paid more than once to the same seller.

    Reported as a ceiling, not a promise: sellers are not obliged to combine
    postage, so this says what could be saved, not what will be.
    """
    by_seller: dict[tuple, list[Listing]] = {}
    for item in cart:
        listing = item.listing
        if listing.seller is None or not listing.shipping_cost:
            continue
        by_seller.setdefault((listing.store, listing.seller), []).append(listing)

    flags = []
    for (_, seller), listings in by_seller.items():
        if len(listings) < 2:
            continue
        postage = [listing.shipping_cost for listing in listings]
        saving = sum(postage, Decimal(0)) - max(postage)
        if saving <= 0:
            continue
        flags.append(
            CartFlag(
                kind="shipping_consolidation",
                message=(
                    f"{len(listings)} items from {seller} are shipping separately. "
                    f"Asking for combined postage could save up to {saving}."
                ),
                saves=saving,
            )
        )
    return flags


def check(cart: list[CartItem], alternatives: list[Listing] | None = None) -> list[CartFlag]:
    """Every saving and mistake the rules can prove, largest saving first."""
    flags = _duplicates(cart) + _cheaper_elsewhere(cart, alternatives or []) + _split_shipping(cart)
    return sorted(flags, key=lambda flag: flag.saves or Decimal(0), reverse=True)


def narrate(flags: list[CartFlag]) -> str:
    """Write the proved findings up as one recommendation.

    The model is given the findings and asked only to phrase them. It is never
    asked to work out a saving: the arithmetic is already done and checkable,
    and a model re-deriving it could quietly get it wrong.
    """
    if not flags:
        return "Nothing to flag — the cart looks fine."

    total = sum((flag.saves for flag in flags if flag.saves), Decimal(0))
    findings = "\n".join(
        f"- {flag.message}" + (f" (saves {flag.saves})" if flag.saves else "") for flag in flags
    )
    # The total is computed here, not by the model, so the headline figure is
    # arithmetic rather than a guess.
    findings += f"\n\nTotal of the savings above: {total}"
    response = client.models.generate_content(
        model=MODEL,
        contents=findings,
        config=types.GenerateContentConfig(system_instruction=SYSTEM),
    )
    return response.text.strip()
