# app/utils/rate_limiter.py
import time
from collections import defaultdict

# Simple per-correlation-id limiter: allow N requests per window
WINDOW = 60  # seconds
ALLOW = 12  # requests per window

_store = defaultdict(list)  # cid -> list of timestamps

def allowed(cid: str) -> bool:
    now = time.time()
    window_start = now - WINDOW
    lst = _store[cid]
    # remove old
    while lst and lst[0] < window_start:
        lst.pop(0)
    if len(lst) >= ALLOW:
        return False
    lst.append(now)
    _store[cid] = lst
    return True
