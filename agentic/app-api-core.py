from fastapi import APIRouter, UploadFile, File, Form
from app.utils.correlation import new_correlation_id
from app.db.vector_adapter import VectorAdapter
import openai


router = APIRouter()

@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    cid = new_correlation_id()
    content = await file.read()
    # Temporary: real ingestion comes in Stage 2
    text_len = len(content)
    return {
        "correlation_id": cid,
        "filename": file.filename,
        "size_bytes": text_len,
        "message": "Ingestion stub - Stage 1"
    }
@router.post("/retrieve")
async def retrieve(query: str = Form(...)):
    adapter = VectorAdapter()
    results = await adapter.query(query_text=query)
    return results

@router.post("/rag-answer")
async def rag_answer(query: str = Form(...)):
    adapter = VectorAdapter()
    hits = await adapter.query(query, top_k=3)

    context = "\n\n".join([h["text"] for h in hits])

    prompt = f"""
Use the context below to answer the question. 
If the answer is not in the context, reply with "Not found in documents."

Context:
{context}

Question:
{query}
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.choices[0].message["content"],
        "evidence": hits
    }
