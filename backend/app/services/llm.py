"""Shared LLM client.

Gemini's Flash tier is used because it is permanently free with no card — the
project's cost constraint, not a capability judgement. Every LLM call in the
project goes through this module, so swapping providers means changing this
file and the three agent call sites, not the graph.

Only the three reasoning agents call it. Product Search, Comparison, and
Deal & Coupon are deterministic by design and must not import this.
"""

from google import genai
from google.genai import errors

from app.config import settings

# The provider's error type, re-exported so routes can catch a rate limit or
# outage and degrade gracefully. Swapping providers changes it here, not in the
# routes.
LLMError = errors.APIError

# Free tier is Flash-class only; Pro moved to paid in April 2026.
#
# Pinned rather than using the `gemini-flash-latest` alias so behaviour does not
# shift underneath the agents. Note that appearing in models.list() does not mean
# a model is callable: gemini-2.5-flash lists fine but 404s for new keys.
#
# Free tier allows 5 requests per minute per model. Three LLM agents run per user
# query, so pace or back off rather than retrying in a tight loop.
MODEL = "gemini-3.6-flash"

client = genai.Client(api_key=settings.gemini_api_key)
