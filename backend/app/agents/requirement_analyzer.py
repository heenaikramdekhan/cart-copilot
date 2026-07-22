"""Agent 1 — free text in, structured requirements out."""

from app.graph.state import Requirements
from app.prompts.requirement_analyzer import SYSTEM
from app.services.claude import MODEL, client


def analyze(user_query: str) -> Requirements:
    """Extract requirements from a plain-language shopping request.

    Uses messages.parse so the response is validated against Requirements
    rather than parsed out of free text. Depth is controlled with effort;
    temperature and budget_tokens are rejected on this model.
    """
    response = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": SYSTEM,
                # No-op until this prompt exceeds the model's minimum cacheable
                # prefix, but correct as the prompt grows.
                "cache_control": {"type": "ephemeral"},
            }
        ],
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        output_format=Requirements,
        messages=[{"role": "user", "content": user_query}],
    )
    return response.parsed_output
