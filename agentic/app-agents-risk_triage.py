from app.agents.base import BaseAgent

class RiskTriageAgent(BaseAgent):
    name = "RiskTriageAgent"

    async def run(self, state):
        missing_docs = state.context.get("missing_documents", [])
        
        risk = "High" if missing_docs else "Low"

        output = {
            "risk_level": risk,
            "reason": "Missing critical evidence" if missing_docs else "All required documents present"
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)

        return state
