"""The one object that flows through the agent graph.

Each agent reads the sections before it and writes only its own. Nothing is
passed between agents as free text, so every handoff stays inspectable.

Optional fields are None until the agent that owns them has run. Lists start
empty rather than None so downstream agents can iterate without guarding.
"""

from decimal import Decimal

from pydantic import BaseModel, Field

from app.services.stores.models import Listing


class Requirements(BaseModel):
    """Agent 1 — Requirement Analyzer.

    This is the schema Claude fills in, so every field has to survive JSON
    Schema. `budget` is a float rather than a Decimal for that reason — it is a
    threshold the user stated, not money being summed. Prices stay Decimal.
    """

    category: str | None = Field(default=None, description="Product category, e.g. 'laptop', 'mouse'")
    budget: float | None = Field(default=None, description="Maximum the user will spend, in USD")
    must_have: list[str] = Field(default_factory=list, description="Hard requirements")
    nice_to_have: list[str] = Field(default_factory=list, description="Preferences")


class ReviewSummary(BaseModel):
    """Agent 4 — Review Intelligence.

    `based_on` and `corpus_through` exist so the UI can state how much real
    review text backs a summary and how old it is. A summary drawn from three
    reviews must not look like one drawn from three hundred.
    """

    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    based_on: int
    corpus_through: str
    average_rating: float | None = None


class CartItem(BaseModel):
    listing: Listing
    quantity: int = 1


class CartFlag(BaseModel):
    """Agent 5 — Cart Optimization. One actionable observation about the cart."""

    kind: str
    message: str
    saves: Decimal | None = None


class Deal(BaseModel):
    """Agent 6 — Deal & Coupon. A discount the store itself reports.

    Real stores do not publish their coupon rules, so this agent surfaces the
    discount data eBay already returns on a listing rather than matching against
    invented rules. Nothing here is inferred.
    """

    store_item_id: str
    kind: str  # "markdown" | "coupon_available"
    original_price: Decimal | None = None
    discount_percent: int | None = None


class AgentState(BaseModel):
    user_query: str

    requirements: Requirements | None = None
    search_results: list[Listing] = Field(default_factory=list)
    ranked_products: list[Listing] = Field(default_factory=list)
    # Keyed by Listing.store_item_id.
    review_summaries: dict[str, ReviewSummary] = Field(default_factory=dict)

    cart: list[CartItem] = Field(default_factory=list)
    cart_flags: list[CartFlag] = Field(default_factory=list)
    deals: list[Deal] = Field(default_factory=list)
