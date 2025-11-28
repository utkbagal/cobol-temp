# app/utils/intent.py
import re
from typing import Tuple
from app.utils.llm_client import chat_with_backoff
from app.utils.observability import track_event

# Simple rule-based patterns for immediate classification
INTENT_PATTERNS = {
    "file_claim": [
        r"\bfile (a )?claim\b", r"\bi want to file\b", r"\bsubmit (a )?claim\b"
    ],
    "qna": [
        r"\bwhat\b", r"\bwho\b", r"\bwhen\b", r"\bwhere\b", r"\bwhich\b", r"\bhow\b", r"\bdoes\b", r"\bdo(es)?\b"
    ],
    "view_policy": [r"\bpolicy\b", r"\bcoverage\b"],
    "claim_status": [r"\bclaim status\b", r"\bstatus of claim\b", r"\bcheck claim\b"],
    "notify": [r"\bnotify\b", r"\bsend notification\b"]
}

# fallback LLM template
LLM_INTENT_PROMPT = """
You are an intent classifier for an insurance claim assistant. Classify the user's intent into one of:
[file_claim, qna, view_policy, claim_status, notify, unknown, malicious]

Return a single JSON object: {{"intent":"<intent>", "confidence": <0.0-1.0>, "explanation":"short"}}
User message:
\"\"\"{message}\"\"\"
"""

def rule_based_intent(message: str) -> Tuple[str, float]:
    text = message.lower()
    counts = {}
    for intent, pats in INTENT_PATTERNS.items():
        for p in pats:
            if re.search(p, text):
                counts[intent] = counts.get(intent, 0) + 1
    if not counts:
        return ("unknown", 0.0)
    # pick highest count
    intent = max(counts, key=lambda k: counts[k])
    return (intent, min(0.8, 0.3 + 0.2 * counts[intent]))


async def detect_intent(message: str, correlation_id: str = "none") -> dict:
    intent, score = rule_based_intent(message)
    track_event("intent_rule_result", correlation_id, {"intent": intent, "score": score})
    if intent != "unknown" and score >= 0.5:
        return {"intent": intent, "confidence": score, "source": "rule"}
    # fallback to LLM classifier for ambiguous cases
    try:
        prompt = LLM_INTENT_PROMPT.format(message=message)
        resp = chat_with_backoff([{"role":"user", "content": prompt}], correlation_id)
        # new SDK: resp.choices[0].message.content
        raw = resp.choices[0].message.content.strip()
        # Expect JSON — attempt parse
        import json
        parsed = json.loads(raw)
        track_event("intent_llm_result", correlation_id, {"parsed": parsed})
        return {"intent": parsed.get("intent", "unknown"), "confidence": parsed.get("confidence", 0.0), "source": "llm"}
    except Exception as e:
        track_event("intent_llm_error", correlation_id, {"error": str(e)})
        # fallback to unknown
        return {"intent": "unknown", "confidence": 0.0, "source": "fallback"}
