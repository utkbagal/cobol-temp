from app.agents.models import OrchestratorState
from app.agents.intake import IntakeAgent
from app.agents.compliance import ComplianceAgent
from app.agents.summarization import SummarizationAgent
from app.agents.risk_triage import RiskTriageAgent

class Orchestrator:
    def __init__(self, correlation_id: str):
        self.state = OrchestratorState(correlation_id=correlation_id)

        self.agents = [
            IntakeAgent(),
            ComplianceAgent(),
            SummarizationAgent(),
            RiskTriageAgent()
        ]

    async def run(self):
        for agent in self.agents:
            self.state = await agent.run(self.state)
        return self.state
