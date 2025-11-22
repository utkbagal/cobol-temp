
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from fastapi import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f">>> Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"<<< Response: {response.status_code} {request.url}")
        return response
