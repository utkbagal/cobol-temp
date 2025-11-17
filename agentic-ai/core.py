##app/api/core.py 

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.rag.ingestion import ingest_document
from app.utils.correlation import new_correlation_id

router = APIRouter()

@router.post("/ingest")
async def ingest(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    cid = new_correlation_id()
    # Save and queue ingestion background task
    content = await file.read()
    # For stage1: call ingestion inline
    result = await ingest_document(content, filename=file.filename, correlation_id=cid)
    return {"correlation_id": cid, "ingest": result}
