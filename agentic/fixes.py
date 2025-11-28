# app/db/vector_adapter.py
async def query(self, query_text, cid=None, source=None, top_k=5):
    # Build proper Chroma filter
    metadata_filter = None

    filters = []
    if cid:
        filters.append({"cid": {"$eq": cid}})
    if source:
        filters.append({"source": {"$eq": source}})

    if len(filters) == 1:
        metadata_filter = filters[0]
    elif len(filters) > 1:
        metadata_filter = {"$and": filters}

    results = self.collection.query(
        query_texts=[query_text],
        n_results=top_k,
        where=metadata_filter
    )
    return results
------

# app/rag/retriever.py
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
