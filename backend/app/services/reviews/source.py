"""Look up real reviews for a live store listing.

The whole review layer sits behind `find_reviews` so the corpus can later be
swapped for a live-review provider without touching the agents. Callers get the
match reason and the recency of the data back, because both have to be shown to
the user rather than implied.
"""

from dataclasses import dataclass

from supabase import create_client

from app.config import settings

# The corpus snapshot ends here; surface it wherever reviews are displayed.
CORPUS_THROUGH = "2023-09"

_client = create_client(settings.supabase_url, settings.supabase_service_key)


@dataclass
class ReviewMatch:
    parent_asin: str
    title: str
    matched_on: str
    average_rating: float | None
    rating_number: int | None
    reviews: list[dict]

    @property
    def corpus_through(self) -> str:
        return CORPUS_THROUGH


def find_reviews(
    brand: str | None,
    model_number: str | None,
    limit: int = 50,
) -> ReviewMatch | None:
    """Reviews for the product a listing refers to, or None if it is unmatched.

    Matching is exact on model number, narrowed by brand when the listing gives
    one. Nothing is matched on title similarity — a wrong match would attach one
    product's reviews to another, which is worse than showing no reviews.
    """
    if not model_number:
        return None

    query = _client.table("products").select(
        "parent_asin,title,average_rating,rating_number"
    ).eq("model_number", model_number)
    if brand:
        query = query.ilike("brand", brand)

    products = query.limit(2).execute().data
    # More than one product shares this model number: too ambiguous to trust.
    if len(products) != 1:
        return None

    product = products[0]
    reviews = (
        _client.table("reviews")
        .select("rating,title,body,helpful_vote,verified_purchase,reviewed_at")
        .eq("parent_asin", product["parent_asin"])
        .order("helpful_vote", desc=True)
        .limit(limit)
        .execute()
        .data
    )
    if not reviews:
        return None

    return ReviewMatch(
        parent_asin=product["parent_asin"],
        title=product["title"],
        matched_on="brand+model_number" if brand else "model_number",
        average_rating=product["average_rating"],
        rating_number=product["rating_number"],
        reviews=reviews,
    )
