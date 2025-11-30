from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_for_claim
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import INTAKE_EXTRACTION_PROMPT
from app.utils.observability import Timer, track_event
from app.utils.formatter import format_as_bullet_list

class IntakeAgent(BaseAgent):
    name = "IntakeAgent"

    async def run(self, state):
        cid = state.correlation_id

        # 1) Retrieve all chunks belonging to this claim
        with Timer("intake_rag_query", cid):
            hits = await retrieve_for_claim(cid=cid, k=8)
        #track_event("retrieve for claim",cid,{"hits":len(hits)})
        list_of_documents = hits.get('documents', []) 
        documents_flat_list = list_of_documents[0] if list_of_documents else []
        context = "\n\n".join([doc for doc in documents_flat_list])
        #track_event("after retrieve for claim",cid,{"context":context})

        prompt = INTAKE_EXTRACTION_PROMPT.format(context=context)

        # 2) Extract metadata from LLM
        resp = chat_with_backoff(
            [{"role": "user", "content": prompt}],
            cid,
            response_format={"type": "json_object"}
        )
        extracted = resp.choices[0].message.content.strip()
        extracted_formatted = format_as_bullet_list(extracted)

        output = {
            "agent_output": extracted_formatted,
            "hits": hits
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context["extracted_metadata"] = extracted
        state.context["rag_hits"] = hits

        return state
