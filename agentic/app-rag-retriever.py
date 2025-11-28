from app.db.vector_adapter import VectorAdapter

adapter = VectorAdapter()

async def retrieve_for_claim(cid: str, k: int = 6):
    """Retrieve chunks for claim processing pipeline (all chunks for correlation_id)."""
    results = await adapter.query(
        query_text="",  # use empty or generic query
        top_k=k,
        metadata_filter={"cid": cid}
    )
    return results


async def retrieve_by_semantic(query: str, cid: str = None, source: str = None, k: int = 5):
    """General semantic retrieval for QnA or agent reasoning."""
    where = {}

    if cid:
        where["cid"] = cid
    if source:
        where["source"] = source

    results = await adapter.query(
        query_text=query,
        top_k=k,
        metadata_filter=where if where else None
    )
    return results
