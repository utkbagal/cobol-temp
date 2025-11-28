# app/agents/qna_agent.py
from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_by_query
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import QA_AGENT_PROMPT, QA_TOOL_FUSION_PROMPT
from app.agents.tools import policy_lookup, claim_status
from app.utils.observability import Timer, track_event
import json

class QnAAgent(BaseAgent):
    name = "QnAAgent"

    async def run(self, state):
        cid = state.correlation_id
        query = state.context.get("user_query")
        filename = state.context.get("filename")

        if not query:
            raise ValueError("QnAAgent: Missing user_query")

        # 1) RAG retrieval
        with Timer("qna_rag_retrieve", cid):
            hits = await retrieve_by_query(query, top_k=5, source=filename)

        rag_context = "\n\n".join([h["text"] for h in hits])

        # 2) Try to answer from RAG
        rag_prompt = QA_AGENT_PROMPT.format(context=rag_context, query=query)
        resp = chat_with_backoff([{"role": "user", "content": rag_prompt}], cid)
        rag_answer = resp.choices[0].message.content.strip()

        tool_data = {}
        tool_used = None

        # 3) If RAG says "Not found", escalate to tools
        if rag_answer.lower() == "not found in documents.":
            # Detect which tool is needed
            if "policy" in query.lower():
                tool_used = "policy_lookup"
                policy_id = state.context.get("extracted_metadata", {}).get("policy_number")
                with Timer("qna_policy_tool", cid):
                    tool_data = await policy_lookup(policy_id)

            elif "claim" in query.lower() and "status" in query.lower():
                tool_used = "claim_status"
                claim_id = state.context.get("extracted_metadata", {}).get("claim_id")
                with Timer("qna_claim_status_tool", cid):
                    tool_data = await claim_status(claim_id)

            else:
                # fallback
                tool_used = None

            # 4) Fuse tool result using LLM
            fusion_prompt = QA_TOOL_FUSION_PROMPT.format(
                query=query,
                tool_name=tool_used,
                tool_data=json.dumps(tool_data, indent=2)
            )
            resp2 = chat_with_backoff([{"role": "user", "content": fusion_prompt}], cid)
            final_answer = resp2.choices[0].message.content.strip()

        else:
            # RAG-only answer is valid
            final_answer = rag_answer

        # 5) Save output
        result = {
            "query": query,
            "rag_answer": rag_answer,
            "tool_used": tool_used,
            "tool_data": tool_data,
            "final_answer": final_answer,
            "evidence": hits
        }

        state.steps.append({"agent": self.name, "output": result})
        state.context["qna_result"] = result

        track_event("agent_completed", cid, {"agent": self.name})

        return state
