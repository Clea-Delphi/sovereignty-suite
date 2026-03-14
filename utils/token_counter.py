#!/usr/bin/env python3
"""
Token counting utilities — approximate, no external deps.
Uses simple heuristics: ~4 characters per token for English, plus special cases.
"""

def estimate_tokens(text: str) -> int:
    """Estimate number of tokens in a string. Roughly 4 chars per token, or 0.75 words per token."""
    # Avoid heavy processing; use fast approximations
    if not text:
        return 0
    # Method 1: word count based (typical: 0.75 tokens per word)
    words = len(text.split())
    approx = int(words * 1.33)  # ~3/4, so words * (4/3) ≈ 1.33
    # Method 2: char count based (average 4 chars per token)
    chars = len(text)
    approx2 = chars // 4
    # Average the two
    return (approx + approx2) // 2

def estimate_cost(tokens: int, price_per_1m_tokens: float = 0.0) -> float:
    """Return estimated cost in USD for given token count at the specified rate."""
    if price_per_1m_tokens <= 0:
        return 0.0
    return (tokens / 1_000_000) * price_per_1m_tokens

# Example usage:
# tokens = estimate_tokens("Hello world!")
# cost = estimate_cost(tokens, 0.50)  # $0.50 per million tokens
