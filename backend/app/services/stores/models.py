from decimal import Decimal

from pydantic import BaseModel


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

    # Product identity, used to join listings to reviews. Populated by the
    # store's detail call, not by search results.
    gtin: str | None = None
    mpn: str | None = None
    brand: str | None = None

    @property
    def total_cost(self) -> Decimal | None:
        """Price plus shipping, or None if shipping is unknown."""
        if self.shipping_cost is None:
            return None
        return self.price + self.shipping_cost
