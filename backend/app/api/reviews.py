"""Review route — real customer reviews for one product, summarized.

Returns 404 rather than an empty summary when nothing matches. A product with
no review match is a different thing from a product reviewers disliked, and the
UI has to be able to tell them apart.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.review_intelligence import summarize
from app.graph.state import ReviewSummary
from app.services.reviews.source import find_reviews

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class ReviewResponse(BaseModel):
    product_title: str
    matched_on: str
    summary: ReviewSummary


@router.get("", response_model=ReviewResponse)
def product_reviews(model_number: str, brand: str | None = None) -> ReviewResponse:
    match = find_reviews(brand, model_number)
    if match is None:
        raise HTTPException(
            status_code=404,
            detail="No reviewed product matches that brand and model number",
        )

    return ReviewResponse(
        product_title=match.title,
        matched_on=match.matched_on,
        summary=summarize(match),
    )
