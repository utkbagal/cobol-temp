##app/utils/logging_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from loguru import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get("x-correlation-id", "unknown")
        logger.info(f"REQ start {request.method} {request.url} cid={cid}")
        response = await call_next(request)
        logger.info(f"REQ end {request.method} {request.url} status={response.status_code} cid={cid}")
        return response
