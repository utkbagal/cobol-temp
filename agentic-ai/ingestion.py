##app/rag/ingestion.py

import asyncio
from typing import Dict
from app.utils.correlation import with_correlation
from app.db.vector_adapter import VectorAdapter

async def simple_text_extractor(bytes_content: bytes, filename: str) -> str:
    # Stage1: naive text decode. Expand to PDF/DOCX parsing with pdfplumber, python-docx later.
    try:
        return bytes_content.decode('utf-8', errors='ignore')
    except Exception:
        return ""

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

@with_correlation
async def ingest_document(bytes_content: bytes, filename: str, correlation_id: str = None) -> Dict:
    text = await simple_text_extractor(bytes_content, filename)
    chunks = chunk_text(text)
    adapter = VectorAdapter()
    ids = await adapter.add_documents([{"text": c, "metadata": {"source": filename}} for c in chunks])
    return {"chunks": len(chunks), "stored_ids": ids}
