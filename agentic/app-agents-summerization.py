import openai
from app.agents.base import BaseAgent

class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    async def run(self, state):
        policy_data = state.context.get("policy_data", {})
        missing_docs = state.context.get("missing_documents", [])

        prompt = f"""
Provide a clear, concise claim summary based on:
- Policy Data: {policy_data}
- Missing Documents: {missing_docs}

Do NOT include chain-of-thought.
Return a short professional summary.
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.choices[0].message["content"]

        output = {"summary": summary}

        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)

        return state
