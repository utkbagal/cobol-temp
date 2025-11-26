from app.agents.base import BaseAgent
from app.agents.tools import policy_lookup

class IntakeAgent(BaseAgent):
    name = "IntakeAgent"

    async def run(self, state):
        filename = state.context.get("filename", "unknown")

        # Placeholder: extract claim ID / policy ID from filename
        policy_id = "POL123"   # Real extraction later from Stage 4 UI

        policy_data = await policy_lookup(policy_id)

        output = {
            "detected_policy_id": policy_id,
            "policy_data": policy_data,
            "missing_fields": ["claim_description", "incident_date"]  # placeholder
        }

        state.steps.append({"agent": self.name, "output": output})
        state.context.update(output)

        return state
