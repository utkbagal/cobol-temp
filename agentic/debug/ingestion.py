# app/rag/ingestion.py
import uuid
from typing import Dict, Any
from app.rag.extractors import extract_text
from app.rag.cleaners import mask_pii
from app.rag.chunker import chunk_text
from app.db.vector_adapter import VectorAdapter
from app.rag.embeddings import embed_text
from app.utils.correlation import new_correlation_id


async def ingest_document(filename: str, bytes_content: bytes, doc_type:str ,correlation_id: str = None) -> Dict[str, Any]:
    cid = correlation_id or new_correlation_id()

    # 1) Extract text
    raw_text = await extract_text(bytes_content, filename)

    # 2) Clean & mask
    cleaned = mask_pii(raw_text)

    # 3) Chunk (token-aware)
    chunks = chunk_text(cleaned, max_tokens=1200, overlap=200)

    # 4) Embed each chunk
    embeddings = []
    for c in chunks:
        emb = await embed_text(c)
        embeddings.append(emb)

    # 5) Store in vector DB
    adapter = VectorAdapter()
    docs = []
    for idx, c in enumerate(chunks):
        docs.append({
            "text": c,
            "metadata": {
                "source": filename,
                "doc_type": doc_type,
                "cid": cid,
                "chunk_index": idx
            }
        })

    ids = await adapter.add_documents(docs=docs, embeddings=embeddings)

    return {
        "correlation_id": cid,
        "chunks": len(chunks),
        "stored_ids": ids
    }