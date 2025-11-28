from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_for_claim
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import INTAKE_EXTRACTION_PROMPT
from app.utils.observability import Timer, track_event

class IntakeAgent(BaseAgent):
    name = "IntakeAgent"

    async def run(self, state):
        cid = state.correlation_id

        # 1) Retrieve all chunks belonging to this claim
        with Timer("intake_rag_query", cid):
            hits = await retrieve_for_claim(cid=cid, k=8)

        context = "\n\n".join([h["text"] for h in hits])

        prompt = INTAKE_EXTRACTION_PROMPT.format(context=context)

        # 2) Extract metadata from LLM
        resp = chat_with_backoff(
            [{"role": "user", "content": prompt}],
            cid
        )
        extracted = resp.choices[0].message.content.strip()

        output = {
            "hits": hits,
            "extracted_metadata": extracted
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context["extracted_metadata"] = extracted
        state.context["rag_hits"] = hits

        return state
