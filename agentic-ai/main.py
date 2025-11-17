##app/main.py

from fastapi import FastAPI, Request
from app.api.core import router as core_router
from app.api.tools import router as tool_router
from app.utils.logging_middleware import LoggingMiddleware

app = FastAPI(title="MACIS Core Service")

app.add_middleware(LoggingMiddleware)

app.include_router(core_router, prefix="/api")
app.include_router(tool_router, prefix="/tools")

@app.get("/health")
async def health():
    return {"status": "ok"}
