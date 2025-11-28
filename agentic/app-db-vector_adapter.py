# app/db/vector_adapter.py

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

    async def query(self, query_text: str, top_k: int = 5, metadata_filter: dict = None):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=metadata_filter
        )

        hits = []
        for i in range(len(results["documents"][0])):
            hits.append({
                "text": results["documents"][0][i],
                "score": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })
        return hits
