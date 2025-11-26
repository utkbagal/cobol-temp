# app/utils/llm_client.py
import openai
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.utils.observability import track_event

openai.api_key = os.getenv("OPENAI_API_KEY")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "25"))  # seconds

# Retry on transient network/timeout errors
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def chat_with_backoff(messages, correlation_id: str):
    track_event("LLM_call_start", correlation_id, {"model": LLM_MODEL})
    resp = openai.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        request_timeout=LLM_TIMEOUT
    )
    track_event("LLM_call_end", correlation_id, {"status": "ok"})
    return resp
