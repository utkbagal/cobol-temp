from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_for_claim
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import SUMMARIZE_PROMPT

class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    async def run(self, state):
        cid = state.correlation_id

        hits = await retrieve_for_claim(cid, k=8)
        context = "\n\n".join([h["text"] for h in hits])

        prompt = SUMMARIZE_PROMPT.format(context=context)

        resp = chat_with_backoff([{"role":"user","content":prompt}], cid)
        summary = resp.choices[0].message.content.strip()

        output = {
            "summary": summary,
            "evidence": hits
        }

        state.steps.append({"agent":self.name,"output":output})
        state.context["summary"] = summary

        return state
