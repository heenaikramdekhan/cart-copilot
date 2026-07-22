"""Shared Anthropic client.

Only the three reasoning agents call Claude. Product Search, Comparison, and
Deal & Coupon are deterministic by design and must not import this.
"""

from anthropic import Anthropic

from app.config import settings

MODEL = "claude-opus-4-8"

client = Anthropic(api_key=settings.anthropic_api_key)
