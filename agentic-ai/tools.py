##app/api/tools.py

from fastapi import APIRouter, HTTPException

router = APIRouter()

# A very small in-memory policy store for stage1 demo
POLICIES = {
    "POL123": {"policy_id": "POL123", "holder": "Alice", "coverages": ["fire", "theft"], "effective": "2024-01-01"},
    "POL456": {"policy_id": "POL456", "holder": "Bob", "coverages": ["accident"], "effective": "2023-06-01"}
}

@router.get("/policy/{policy_id}")
async def get_policy(policy_id: str):
    p = POLICIES.get(policy_id)
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    return p

@router.get("/claim/{claim_id}/status")
async def claim_status(claim_id: str):
    return {"claim_id": claim_id, "status": "open", "last_update": "2025-01-01"}
