from fastapi import FastAPI
from app.api.core import router as core_router
from app.api.tools import router as tools_router
from app.utils.logging_middleware import LoggingMiddleware

app = FastAPI(title="MACIS Core Service")

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(core_router, prefix="/api")
app.include_router(tools_router, prefix="/tools")

@app.get("/health")
async def health():
    return {"status": "ok"}
