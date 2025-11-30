from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_for_claim
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import SUMMARY_PROMPT
from app.utils.observability import Timer, track_event

class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    async def run(self, state):
        cid = state.correlation_id

        hits = await retrieve_for_claim(cid=cid, k=8)
        track_event("SUMMARY*****",cid,{"hits":hits})
        list_of_documents = hits.get('documents', []) 
        track_event("SUMMARY*****",cid,{"hits":list_of_documents})
        documents_flat_list = list_of_documents[0] if list_of_documents else []
        track_event("SUMMARY*****",cid,{"hits":documents_flat_list})

        context1 = "\n\n".join([doc for doc in documents_flat_list])
        track_event("SUMMARY*****",cid,{"hits":context1})
        context2 = "\n\n".join([str(agent_ouput.get("agent_output")) for agent_ouput in state.steps[-4:]])
        track_event("SUMMARY*****",cid,{"hits":context2})
        context = context1 + context2
        prompt = SUMMARY_PROMPT.format(context=context)

        resp = chat_with_backoff(
            [{"role": "user", "content": prompt}],
            cid,
            response_format=None
        )
        summary = resp.choices[0].message.content.strip()
        track_event("SUMMARY*****",cid,{"hits":prompt})
        output = {
            "agent_output": summary,
            "evidence": hits
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context["summary"] = summary

        return state