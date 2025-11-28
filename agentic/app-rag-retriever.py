from chromadb import Client
from chromadb.config import Settings

client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./data/vector_db"))

collection = client.get_or_create_collection("claims")

def retrieve_context(filename: str, k=4):
    results = collection.query(
        query_texts=[filename],  # or query by document title
        n_results=k
    )
    out = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        out.append({"text": text, "metadata": meta})
    return out
