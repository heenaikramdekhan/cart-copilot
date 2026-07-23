"""Agent 4 — real review text in, pros and cons out."""

from google.genai import types
from pydantic import BaseModel

from app.graph.state import ReviewSummary
from app.prompts.review_intelligence import SYSTEM
from app.services.llm import MODEL, client
from app.services.reviews.source import ReviewMatch

# Longer reviews are trimmed: the useful judgement is almost always up front,
# and 50 full reviews is a lot of tokens for no extra signal.
MAX_REVIEW_CHARS = 800


class _ProsCons(BaseModel):
    """What the model is asked for — deliberately just the opinion.

    Provenance (how many reviews, how old, the average rating) is known from
    the database and is filled in by this module. Asking the model to report
    its own evidence count invites it to be wrong about it.
    """

    pros: list[str]
    cons: list[str]


def _format(reviews: list[dict]) -> str:
    lines = []
    for review in reviews:
        title = review["title"] or ""
        body = review["body"][:MAX_REVIEW_CHARS].replace("\n", " ")
        lines.append(f"[{review['rating']}/5] {title}: {body}")
    return "\n\n".join(lines)


def summarize(match: ReviewMatch) -> ReviewSummary:
    """Summarize one product's reviews into pros and cons."""
    response = client.models.generate_content(
        model=MODEL,
        contents=_format(match.reviews),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            response_mime_type="application/json",
            response_schema=_ProsCons,
        ),
    )
    opinion = response.parsed

    return ReviewSummary(
        pros=opinion.pros,
        cons=opinion.cons,
        based_on=len(match.reviews),
        corpus_through=match.corpus_through,
        average_rating=match.average_rating,
    )
