from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import AgentState


class MemoryManager:
    def __init__(self):
        self.checkpointer = InMemorySaver()
        pass

    def get_checkpointer(self):
        return self.checkpointer

    pass


class KarmaAgentState(AgentState):
    user_name: str
    pass
