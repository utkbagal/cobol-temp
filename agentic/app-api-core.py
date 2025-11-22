from fastapi import APIRouter, UploadFile, File, Form
from app.utils.correlation import new_correlation_id
from app.db.vector_adapter import VectorAdapter

router = APIRouter()

@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    cid = new_correlation_id()
    content = await file.read()
    # Temporary: real ingestion comes in Stage 2
    text_len = len(content)
    return {
        "correlation_id": cid,
        "filename": file.filename,
        "size_bytes": text_len,
        "message": "Ingestion stub - Stage 1"
    }
@router.post("/retrieve")
async def retrieve(query: str = Form(...)):
    adapter = VectorAdapter()
    results = await adapter.query(query_text=query)
    return results
