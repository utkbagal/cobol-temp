# app/rag/embeddings.py
import os

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_KEY:
    import openai
    openai.api_key = OPENAI_KEY
    EMBED_MODEL = "text-embedding-3-small"

    async def embed_text(text: str) -> list[float]:
        # sync call inside async – acceptable for dev; replace with threadpool for production
        resp = openai.embeddings.create(input=text, model=EMBED_MODEL)
        return resp.data[0].embedding
else:
    # fallback local model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")

    async def embed_text(text: str) -> list[float]:
        vec = model.encode(text)
        return vec.tolist()
