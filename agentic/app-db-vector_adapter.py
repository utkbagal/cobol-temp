# app/db/vector_adapter.py
import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Optional

class VectorAdapter:
    def __init__(self, persist_directory: str = "./data/vector_db"):
        self.client = chromadb.Client(
            Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory)
        )
        # collection name
        self.collection = self.client.get_or_create_collection(
            name="macis_docs",
            metadata={"hnsw:space": "cosine"}
        )

    def _new_id(self):
        return str(uuid.uuid4())

    async def add_documents(self, docs: List[Dict], embeddings: List[List[float]] = None) -> List[str]:
        """
        docs: list of {"text": ..., "metadata": {...}}
        embeddings: list of vectors aligned with docs (optional if Chromadb computes embeddings)
        """
        ids = [self._new_id() for _ in docs]
        texts = [d["text"] for d in docs]
        metadatas = [d.get("metadata", {}) for d in docs]

        if embeddings:
            # Chromadb expects embeddings param as list of lists
            self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        else:
            self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return ids

    async def query(self, query_text: str, top_k: int = 5, metadata_filter: Optional[Dict] = None):
        """
        Query by text. Optionally filter by metadata, for example {'source': 'filename.pdf'}
        """
        # chroma's query takes query_texts and returns results dict
        if metadata_filter:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=metadata_filter
            )
        else:
            results = self.collection.query(query_texts=[query_text], n_results=top_k)

        docs = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        out = []
        for text, dist, meta in zip(docs, distances, metadatas):
            out.append({"text": text, "score": float(dist), "metadata": meta})
        return out
