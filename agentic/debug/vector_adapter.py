import chromadb
from typing import List, Dict

PERSIST_DIR = "data/vector_db"

class VectorAdapter:
    def __init__(self, persist_directory: str = PERSIST_DIR):
        # NEW API — Chroma 0.5+
        self.client = chromadb.PersistentClient(path=persist_directory)

        # create collection if not exists
        self.collection = self.client.get_or_create_collection(
            name="claims",
            metadata={"hnsw:space": "cosine"}  # similarity metric
        )

    async def add_documents(self, docs: List[Dict], embeddings: List[List[float]]):
        ids = []
        metadatas = []
        texts = []

        for i, d in enumerate(docs):
            ids.append(f"{d['metadata']['cid']}_{d['metadata']['chunk_index']}")
            metadatas.append(d["metadata"])
            texts.append(d["text"])

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )

        return ids

    async def query(self, query_text, cid=None,doc_type=None, source=None, top_k=5):
        # Build proper Chroma filter
        metadata_filter = None

        filters = []
        if cid:
            filters.append({"cid": {"$eq": cid}})
        if source:
            filters.append({"source": {"$eq": source}})
        if doc_type:
            filters.append({"doc_type": {"$eq": doc_type}})

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
