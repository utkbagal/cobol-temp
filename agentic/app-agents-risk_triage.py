from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_for_claim
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import RISK_TRIAGE_PROMPT

class RiskTriageAgent(BaseAgent):
    name = "RiskTriageAgent"

    async def run(self, state):
        cid = state.correlation_id
        hits = await retrieve_for_claim(cid, k=8)
        context = "\n\n".join([h["text"] for h in hits])
        extracted = state.context.get("extracted_metadata", "")

        prompt = RISK_TRIAGE_PROMPT.format(context=context, metadata=extracted)

        resp = chat_with_backoff([{"role":"user","content":prompt}], cid)
        triage = resp.choices[0].message.content.strip()

        output = {
            "risk_assessment": triage,
            "evidence": hits
        }

        state.steps.append({"agent":self.name,"output":output})
        state.context["risk_assessment"] = triage

        return state
