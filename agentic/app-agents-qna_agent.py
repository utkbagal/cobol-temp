from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_by_query
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import QA_AGENT_PROMPT
from app.utils.observability import Timer, track_event

class QnAAgent(BaseAgent):
    name = "QnAAgent"

    async def run(self, state):
        cid = state.correlation_id
        user_query = state.context.get("user_query")
        filename = state.context.get("filename")

        if not user_query:
            raise ValueError("QnAAgent: 'user_query' missing from context")

        # 1) Do a RAG search
        with Timer("qna_rag_retrieve", cid):
            hits = await retrieve_by_query(query_text=user_query, top_k=5, source=filename)

        context = "\n\n".join([h["text"] for h in hits])

        prompt = QA_AGENT_PROMPT.format(context=context, query=user_query)

        # 2) LLM answer
        with Timer("qna_llm", cid):
            resp = chat_with_backoff([{"role": "user", "content": prompt}], cid)

        answer = resp.choices[0].message.content.strip()

        output = {"query": user_query, "answer": answer, "evidence": hits}

        # 3) Save step output
        state.steps.append({"agent": self.name, "output": output})
        state.context["qna_result"] = output

        track_event("agent_completed", cid, {"agent": self.name})

        return state
