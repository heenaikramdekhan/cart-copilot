from decimal import Decimal

from pydantic import BaseModel, Field


class Listing(BaseModel):
    """One product offer from one store, normalized across store APIs.

    A field is None when the store did not report it. Never substitute a
    default — an unknown shipping cost is not a free shipping cost.
    """

    store: str
    store_item_id: str
    title: str
    price: Decimal
    currency: str
    url: str

    shipping_cost: Decimal | None = None
    condition: str | None = None
    seller: str | None = None
    image_url: str | None = None

    # Discounts the store itself reports. Agent 6 surfaces these rather than
    # matching against coupon rules, which real retailers do not publish.
    original_price: Decimal | None = None
    discount_percent: int | None = None
    has_coupon: bool = False

    # Product identity, used to join listings to reviews. Populated by the
    # store's detail call, not by search results.
    gtin: str | None = None
    mpn: str | None = None
    brand: str | None = None

    # Store-reported specs, normalized to a flat map. This is the only spec
    # data real listings carry, and it is what Comparison ranks against.
    aspects: dict[str, str] = Field(default_factory=dict)

    @property
    def total_cost(self) -> Decimal | None:
        """Price plus shipping, or None if shipping is unknown."""
        if self.shipping_cost is None:
            return None
        return self.price + self.shipping_cost

    @property
    def cost(self) -> Decimal:
        """What this listing costs for ranking and comparison.

        Falls back to price when shipping is unknown. Use `total_cost` when the
        distinction matters — this one deliberately blurs it so a listing with
        unreported postage can still be ordered against the others.
        """
        return self.total_cost if self.total_cost is not None else self.price
