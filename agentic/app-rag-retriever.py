# app/rag/retriever.py
from app.db.vector_adapter import VectorAdapter

adapter = VectorAdapter()

async def retrieve_by_query(query_text: str, top_k: int = 5, source: str = None):
    if source:
        return await adapter.query(query_text=query_text, top_k=top_k, metadata_filter={"source": source})
    return await adapter.query(query_text=query_text, top_k=top_k)
