from fastapi import APIRouter, HTTPException

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
