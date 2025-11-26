# app/agents/controller.py
from app.agents.models import OrchestratorState
from app.agents.intake import IntakeAgent
from app.agents.compliance import ComplianceAgent
from app.agents.summarization import SummarizationAgent
from app.agents.risk_triage import RiskTriageAgent
from app.utils.observability import Timer, track_event

class Orchestrator:
    def __init__(self, correlation_id: str):
        self.state = OrchestratorState(correlation_id=correlation_id)
        self.agents = [IntakeAgent(), ComplianceAgent(), SummarizationAgent(), RiskTriageAgent()]

    async def run(self):
        cid = self.state.correlation_id
        track_event("orchestrator_start", cid, {})
        for agent in self.agents:
            with Timer(agent.name, cid):
                self.state = await agent.run(self.state)
                track_event("agent_step", cid, {"agent": agent.name, "step_output": self.state.steps[-1].output})
        track_event("orchestrator_end", cid, {})
        return self.state
