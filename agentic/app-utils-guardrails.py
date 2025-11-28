# app/utils/guardrails.py
import re
from typing import Tuple
from app.rag.cleaners import mask_pii

# Profanity/obscene word list (short example); expand as needed
PROFANITY = re.compile(r"\b(shit|damn|bitch|fucker|fuck)\b", re.IGNORECASE)

# prompt-injection patterns: tries to look for 'ignore previous instruction' style
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore (my|previous|earlier) instructions", re.IGNORECASE),
    re.compile(r"disregard (the )?previous", re.IGNORECASE),
    re.compile(r"follow these new instructions", re.IGNORECASE),
    re.compile(r"execute the following", re.IGNORECASE),
]

MAX_INPUT_LENGTH = 4000  # characters

def check_profanity(text: str) -> bool:
    return bool(PROFANITY.search(text))

def check_prompt_injection(text: str) -> Tuple[bool, str]:
    for p in PROMPT_INJECTION_PATTERNS:
        if p.search(text):
            return True, p.pattern
    return False, ""

def enforce_length(text: str) -> str:
    if len(text) > MAX_INPUT_LENGTH:
        return text[:MAX_INPUT_LENGTH] + "\n...[TRUNCATED]"
    return text

def sanitize_user_input(text: str) -> dict:
    """
    Returns dict:
    {
      "ok": bool,
      "sanitized": str,
      "flags": [list of flag strings]
    }
    """
    flags = []
    t = text

    # basic length enforcement
    t = enforce_length(t)

    # PII masking
    t = mask_pii(t)

    # profanity: mask (not reject) — we choose to mask profanity
    if check_profanity(t):
        flags.append("profanity")
        t = PROFANITY.sub("[REDACTED]", t)

    # prompt injection detection: reject strongly
    inj, pattern = check_prompt_injection(t)
    if inj:
        flags.append("prompt_injection")
        return {"ok": False, "sanitized": "", "flags": flags, "reason": "prompt_injection_detected"}

    return {"ok": True, "sanitized": t, "flags": flags}
