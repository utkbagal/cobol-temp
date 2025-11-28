import httpx
from app.api.config import TOOLS_BASE_URL

client = httpx.AsyncClient()

async def policy_lookup(policy_id):
    resp = await client.get(f"{TOOLS_BASE_URL}/policy/{policy_id}")
    return resp.json()

async def claim_status(claim_id):
    resp = await client.get(f"{TOOLS_BASE_URL}/claim/{claim_id}/status")
    return resp.json()

async def send_notification(message: str):
    return {"sent": True, "message": message}  # mock
