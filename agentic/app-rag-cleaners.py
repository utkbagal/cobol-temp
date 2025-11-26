# app/rag/cleaners.py
import re

PII_PATTERNS = [
    (re.compile(r"\b\d{10}\b"), "[PHONE]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
    (re.compile(r"\bPOL[\s\-]?\d+\b", re.IGNORECASE), "[POLICY_NO]"),
    (re.compile(r"\b\d{12}\b"), "[IDENTIFIER]")  # generic long numeric ids
]

def mask_pii(text: str) -> str:
    out = text
    for pat, repl in PII_PATTERNS:
        out = pat.sub(repl, out)
    return out

def sanitize_for_prompt(text: str, max_chars: int = 3000) -> str:
    """Also truncate to avoid over-long prompts."""
    t = mask_pii(text)
    if len(t) > max_chars:
        return t[:max_chars] + "\n...[TRUNCATED]"
    return t
