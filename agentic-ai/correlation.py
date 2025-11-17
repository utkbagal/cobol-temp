##app/utils/correlation.py

import uuid
from functools import wraps

def new_correlation_id():
    return str(uuid.uuid4())

def with_correlation(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        cid = kwargs.get("correlation_id") or new_correlation_id()
        kwargs["correlation_id"] = cid
        return await fn(*args, **kwargs)
    return wrapper
