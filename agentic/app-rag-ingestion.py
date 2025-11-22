from app.rag.extractors import extract_text
from app.rag.cleaners import mask_pii
from app.rag.chunker import chunk_text
from app.db.vector_adapter import VectorAdapter

async def ingest_document(data: bytes, filename: str, correlation_id: str):
    # 1. Extract
    raw_text = await extract_text(data, filename)

    # 2. Clean & mask
    cleaned_text = mask_pii(raw_text)

    # 3. Chunk
    chunks = chunk_text(cleaned_text)

    # 4. Store to vector DB
    adapter = VectorAdapter()
    docs = [{"text": c, "metadata": {"source": filename}} for c in chunks]
    ids = await adapter.add_documents(docs)

    return {
        "chunks": len(chunks),
        "stored_ids": ids,
        "message": "Ingested successfully"
    }
