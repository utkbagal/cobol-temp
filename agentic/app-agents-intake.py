# app/agents/intake.py
from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_by_query
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import INTAKE_EXTRACTION_PROMPT
from app.rag.cleaners import sanitize_for_prompt
from app.utils.observability import Timer, track_event

class IntakeAgent(BaseAgent):
    name = "IntakeAgent"

    async def run(self, state):
        cid = state.correlation_id
        filename = state.context.get("filename")
        # retrieve chunks for this file as context
        with Timer("intake_retrieve", cid):
            hits = await retrieve_by_query(query_text=filename, top_k=6, source=filename)

        context_text = "\n\n".join([h["text"] for h in hits])
        context_text = sanitize_for_prompt(context_text)

        prompt = INTAKE_EXTRACTION_PROMPT.format(context=context_text)

        with Timer("intake_llm", cid):
            resp = chat_with_backoff([{"role": "user", "content": prompt}], cid)

        extracted = resp.choices[0].message.content.strip()

        output = {
            "rag_hits": hits,
            "extracted_metadata": extracted
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context.update({"extracted_metadata": extracted, "rag_hits": hits})
        track_event("agent_completed", cid, {"agent": self.name})
        return state
