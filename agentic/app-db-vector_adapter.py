import chromadb
from chromadb.config import Settings

class VectorAdapter:
    def __init__(self):
        self.client = chromadb.Client(
            Settings(chroma_db_impl="duckdb+parquet", persist_directory="./data/vector_db")
        )
        self.collection = self.client.get_or_create_collection(
            "macis_docs",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_documents(self, docs):
        ids = []
        texts = []
        metadata = []

        for i, d in enumerate(docs):
            ids.append(f"doc_{i}")
            texts.append(d["text"])
            metadata.append(d["metadata"])

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadata
        )

        return ids

    async def query(self, query_text: str, top_k: int = 5):
        result = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return [
            {
                "text": t,
                "score": s,
                "metadata": m
            }
            for t, s, m in zip(result["documents"][0], result["distances"][0], result["metadatas"][0])
        ]
