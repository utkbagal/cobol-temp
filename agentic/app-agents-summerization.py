# app/agents/summarization.py
from app.agents.base import BaseAgent
from app.agents.prompt_templates import SUMMARY_PROMPT
from app.utils.llm_client import chat_with_backoff
from app.utils.observability import Timer, track_event
from app.rag.cleaners import sanitize_for_prompt

class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    async def run(self, state):
        cid = state.correlation_id
        policy_data = state.context.get("policy_data", {})
        missing_docs = state.context.get("missing_documents", [])

        # Build context safely
        context_parts = [
            f"Policy: {policy_data}",
            f"Missing documents: {missing_docs}"
        ]
        context = sanitize_for_prompt("\n".join(context_parts))

        prompt = SUMMARY_PROMPT.format(context=context)

        messages = [{"role": "user", "content": prompt}]

        with Timer("summarization_agent", cid):
            resp = chat_with_backoff(messages, cid)

        summary = resp.choices[0].message["content"].strip()

        output = {"summary": summary}
        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)
        track_event("agent_completed", cid, {"agent": self.name})
        return state
