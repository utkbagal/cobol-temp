##app/db/vector_adapter.py

class VectorAdapter:
    def __init__(self):
        # Later: init Chroma/pgvector client
        pass

    async def add_documents(self, docs):
        # docs: list of {"text":..., "metadata": {...}}
        # For stage1: return fake ids
        return [f"id_{i}" for i in range(len(docs))]

    async def query(self, query_text, k=5, metadata_filter=None):
        # return fake results
        return [{"text": "sample hit", "score": 0.9, "metadata": {}}]
