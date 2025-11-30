from app.db.vector_adapter import VectorAdapter
from app.utils.observability import Timer, track_event

adapter = VectorAdapter()

async def retrieve_for_claim(cid: str, k: int = 6):
    """Retrieve chunks for claim processing pipeline (all chunks for correlation_id)."""
    results = await adapter.query(
        query_text="",  # use empty or generic query
        top_k=k,
        cid=cid,
        doc_type='claim'
    )
    track_event("retrieval-------->",cid,{"results":results})
    return results

async def retrieve_by_semantic(query, cid, source, k=5):
    results = await adapter.query(
        query_text=query,
        cid=cid,
        source=source,
        top_k=k
    )
    
    hits = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for i in range(len(ids)):
        hits.append({
            "text": docs[i],
            "metadata": metas[i],
            "score": float(dists[i]),
        })

    return hits
