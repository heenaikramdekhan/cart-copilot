"""Agent 1 — free text in, structured requirements out."""

from google.genai import types

from app.graph.state import Requirements
from app.prompts.requirement_analyzer import SYSTEM
from app.services.llm import MODEL, client


def analyze(user_query: str) -> Requirements:
    """Extract requirements from a plain-language shopping request.

    The response is constrained to the Requirements schema by the model rather
    than parsed out of free text, so a malformed answer fails here instead of
    somewhere downstream.
    """
    response = client.models.generate_content(
        model=MODEL,
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            response_mime_type="application/json",
            response_schema=Requirements,
        ),
    )
    return response.parsed
