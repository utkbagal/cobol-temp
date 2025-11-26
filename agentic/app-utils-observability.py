# app/utils/observability.py
from loguru import logger
import time
import json

def setup_logging(level="INFO"):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=level, backtrace=False, diagnose=False)

def track_event(event_name: str, correlation_id: str, payload: dict = None):
    payload = payload or {}
    logger.info(json.dumps({
        "event": event_name,
        "cid": correlation_id,
        "payload": payload
    }))

class Timer:
    def __init__(self, name: str, correlation_id: str):
        self.name = name
        self.cid = correlation_id
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - self.start
        track_event(f"{self.name}_latency_ms", self.cid, {"ms": int(elapsed * 1000)})
