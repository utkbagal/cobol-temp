# app/agents/controller.py
from app.agents.models import OrchestratorState
from app.agents.intake import IntakeAgent
from app.agents.compliance import ComplianceAgent
from app.agents.summarization import SummarizationAgent
from app.agents.risk_triage import RiskTriageAgent
from app.agents.qna_agent import QnAAgent
from app.utils.observability import Timer, track_event

class Orchestrator:
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.state = OrchestratorState(correlation_id=correlation_id)

    async def run(self, mode="claim"):
        """
        mode = "claim" → intake → compliance → summary → triage
        mode = "qna"   → only QnAAgent
        """

        if mode == "qna":
            agents = [QnAAgent()]
        else:
            agents = [
                IntakeAgent(),
                ComplianceAgent(),
                SummarizationAgent(),
                RiskTriageAgent()
            ]

        for agent in agents:
            self.state = await agent.run(self.state)

        return self.state
