import httpx

BASE_URL = "http://localhost:8000/tools"

async def policy_lookup(policy_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/policy/{policy_id}")
        return resp.json()

async def claim_status(claim_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/claim/{claim_id}/status")
        return resp.json()

async def send_notification(message: str):
    return {"sent": True, "message": message}  # mock
