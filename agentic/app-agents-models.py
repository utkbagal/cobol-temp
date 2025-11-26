from pydantic import BaseModel
from typing import List, Dict, Any

class AgentMessage(BaseModel):
    agent: str
    output: Dict[str, Any]

class OrchestratorState(BaseModel):
    correlation_id: str
    steps: List[AgentMessage] = []
    context: Dict[str, Any] = {}   # Shared data between agents
