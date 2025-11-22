from fastapi import APIRouter, UploadFile, File
from app.utils.correlation import new_correlation_id

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
