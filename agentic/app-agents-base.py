class BaseAgent:
    name = "BaseAgent"

    async def run(self, state):
        raise NotImplementedError("Agent must implement run()")
