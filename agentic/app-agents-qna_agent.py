from app.agents.base import BaseAgent
from app.rag.retriever import retrieve_by_semantic
from app.utils.llm_client import chat_with_backoff
from app.agents.prompt_templates import QA_AGENT_PROMPT

class QnAAgent(BaseAgent):
    name = "QnAAgent"

    async def run(self, state):
        cid = state.correlation_id
        query = state.context["user_query"]
        filename = state.context["filename"]

        # 1) Semantic search from embeddings
        hits = await retrieve_by_semantic(query=query, cid=cid, source=filename, k=5)
        context = "\n\n".join([h["text"] for h in hits])

        # 2) Pure RAG answer
        prompt = QA_AGENT_PROMPT.format(context=context, query=query)
        resp = chat_with_backoff([{"role":"user","content":prompt}], cid)

        answer = resp.choices[0].message.content.strip()

        output = {
            "query": query,
            "answer": answer,
            "evidence": hits
        }

        state.steps.append({"agent": self.name, "output":output})
        state.context["qna_result"] = output

        return state
