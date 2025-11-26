from fastapi import APIRouter, HTTPException, Body
from app.utils.observability import track_event

router = APIRouter()

POLICIES = {
    "POL123": {"id": "POL123", "holder": "Alice", "coverages": ["fire", "theft"]},
    "POL456": {"id": "POL456", "holder": "Bob", "coverages": ["accident"]}
}

@router.get("/policy/{pid}")
async def get_policy(pid: str):
    p = POLICIES.get(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    return p

@router.post("/notify")
async def notify(payload: dict = Body(...)):
    cid = payload.get("correlation_id", "none")
    message = payload.get("message", "no message")
    # mock send
    track_event("notify_sent", cid, {"message": message})
    return {"status": "sent", "correlation_id": cid, "message": message}
