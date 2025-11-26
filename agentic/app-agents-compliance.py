from app.agents.base import BaseAgent

class ComplianceAgent(BaseAgent):
    name = "ComplianceAgent"

    async def run(self, state):
        required_docs = ["policy document", "incident photos"]
        
        # placeholder: assume only one doc is uploaded
        missing_docs = ["incident photos"]

        output = {
            "required_documents": required_docs,
            "missing_documents": missing_docs,
            "compliance_status": "Partial" if missing_docs else "Complete"
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)

        return state
