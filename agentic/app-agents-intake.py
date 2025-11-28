# app/agents/intake.py
from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_context
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import INTAKE_EXTRACTION_PROMPT
from app.utils.observability import track_event, Timer
from app.rag.cleaners import sanitize_for_prompt

class IntakeAgent(BaseAgent):
    name = "IntakeAgent"

    async def run(self, state):
        cid = state.correlation_id
        filename = state.context.get("filename")

        # 1) Retrieve context from RAG
        with Timer("intake_rag_retrieve", cid):
            rag_results = retrieve_context(filename, k=4)

        merged_text = "\n\n".join([doc["text"] for doc in rag_results])

        safe_text = sanitize_for_prompt(merged_text)

        prompt = INTAKE_EXTRACTION_PROMPT.format(context=safe_text)

        # 2) LLM-based extraction using real document content
        with Timer("intake_llm_extract", cid):
            resp = chat_with_backoff([{"role": "user", "content": prompt}], cid)

        extracted = resp.choices[0].message.content

        output = {
            "rag_context_used": True,
            "retrieved_chunks": rag_results,
            "extracted_metadata": extracted
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)

        return state
