# app/rag/ingestion.py
from app.rag.extractors import extract_text
from app.rag.cleaners import mask_pii
from app.rag.chunker import chunk_text
from app.db.vector_adapter import VectorAdapter
from app.rag.embeddings import embed_text
from app.utils.correlation import new_correlation_id
from typing import Dict, Any

async def ingest_document(bytes_content: bytes, filename: str, correlation_id: str = None) -> Dict[str, Any]:
    cid = correlation_id or new_correlation_id()

    # 1. Extract text
    raw_text = await extract_text(bytes_content, filename)

    # 2. Clean & mask PII
    cleaned = mask_pii(raw_text)

    # 3. Chunk
    chunks = chunk_text(cleaned, max_tokens=1200, overlap=200)

    # 4. Compute embeddings for each chunk (synchronously inside async)
    embeddings = []
    for c in chunks:
        vec = await embed_text(c)
        embeddings.append(vec)

    # 5. Store into vector DB with metadata
    adapter = VectorAdapter()
    docs = [{"text": c, "metadata": {"source": filename, "correlation_id": cid}} for c in chunks]
    ids = await adapter.add_documents(docs, embeddings=embeddings)

    return {"correlation_id": cid, "chunks": len(chunks), "stored_ids": ids}
