import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

async def embed_text(text: str) -> list[float]:
    response = openai.embeddings.create(
        input=text,
        model=EMBED_MODEL
    )
    return response.data[0].embedding
