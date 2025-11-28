from fastapi import APIRouter, UploadFile, File, Form, Body
from app.utils.correlation import new_correlation_id
from app.db.vector_adapter import VectorAdapter
from app.agents.controller import Orchestrator
import openai
from app.rag.extractors import extract_text
from app.rag.cleaners import mask_pii
from app.rag.chunker import chunk_text
from app.db.vector_adapter import VectorAdapter
from app.rag.embeddings import embed_text
from typing import Dict, Any

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
async def retrieve(query: str = Body(...)):
    results = await retrieve_by_query(query, top_k=5)
    return {"hits": results}

@router.post("/rag-answer")
async def rag_answer(payload: dict = Body(...)):
    query = payload.get("query")
    source = payload.get("source")  # optional: filename to restrict
    hits = await retrieve_by_query(query, top_k=5, source=source) if source else await retrieve_by_query(query, top_k=5)

    # build context string with source captions
    context = "\n\n".join([f"[source: {h['metadata'].get('source','unknown')}]\n{h['text']}" for h in hits])

    prompt = RAG_ANSWER_PROMPT.format(context=context, query=query)

    resp = chat_with_backoff([{"role": "user", "content": prompt}], payload.get("correlation_id", "none"))
    # new SDK: resp.choices[0].message.content
    answer = resp.choices[0].message.content.strip()

    return {"answer": answer, "evidence": hits}

@router.post("/claims/process")
async def process_claim(filename: str = Form(...)):
    cid = new_correlation_id()
    
    orch = Orchestrator(correlation_id=cid)
    orch.state.context["filename"] = filename  # placeholder for metadata

    result = await orch.run()

    return result.dict()

@router.post("/claims/rerun_triage")
async def rerun_triage(payload: dict = Body(...)):
    cid = payload.get("correlation_id")
    if not cid:
        return {"error": "correlation_id required"}, 400
    # Recreate orchestrator but only run risk triage agent
    orch = Orchestrator(correlation_id=cid)
    # optionally preload state from DB (we're in-memory for now)
    # For now: run whole pipeline again but in real impl we'd persist and resume
    result = await orch.run()
    return result.dict()

@router.post("/claims/qna")
async def qna(payload: dict = Body(...)):
    filename = payload.get("filename")
    query = payload.get("query")
    cid = payload.get("correlation_id") or new_correlation_id()

    orch = Orchestrator(correlation_id=cid)
    orch.state.context["filename"] = filename
    orch.state.context["user_query"] = query

    result = await orch.run(mode="qna")

    return result.dict()
