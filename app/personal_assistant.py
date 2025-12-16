from langchain_ollama import ChatOllama
import json
from app.utils.local_types import Config, OutputFormat, output_format_schema
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AnyMessage
from app.access.tools import retrieve_context, update_memory, terminal_access
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
import ast
from app.utils.memory_management import MemoryManager, KarmaAgentState


class Agent:
    def __init__(self, memory_manager: MemoryManager):
        self.config = {}
        self.memory_manager = memory_manager
        self.tools = [
            retrieve_context,
            update_memory,
            terminal_access,
        ]
        self.memory_config = {"configurable": {"thread_id": "1"}}
        self.initialized = False
        self.personal_agent = ""

    def run(self, query: str):
        if not self.initialized:
            self._initialize()
            self.initialized = True
        resp = self.personal_agent.invoke(
            {"messages": HumanMessage(query), "user_name": "Kelvin Gander"},
            self.memory_config,
        )
        self._save_chat_history(
            self.personal_agent.get_state(self.memory_config).values["messages"]
        )
        self._list_tools_used(resp)
        parsed_resp = resp["structured_response"]
        if parsed_resp["goal_achieved"]:
            print("Goal Acheived!")
        return parsed_resp["content"]

    def _initialize(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            self.config = Config(**data)
        custom_profile = {
            "structured_output": True,
            # ...
        }
        llm = ChatOllama(
            model=self.config.model_name,
            temperature=self.config.temperature,
            profile=custom_profile,
        )
        self.personal_agent = create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=self.config.system_message,
            response_format=ToolStrategy(output_format_schema),
            checkpointer=self.memory_manager.get_checkpointer(),
            state_schema=KarmaAgentState,
        )

    def _list_tools_used(self, resp):
        for message in resp["messages"]:
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Tools used: {[tc['name'] for tc in message.tool_calls]}")

            # For AIMessage with tool_calls attribute
            if message.type == "ai" and hasattr(message, "tool_calls"):
                for tool_call in message.tool_calls:
                    print(f"Tool: {tool_call['name']}, Args: {tool_call['args']}")

    def _save_chat_history(self, messages: list[AnyMessage]):
        m = [
            {"role": message.type, "content": message.content}
            for message in messages
            if message.content
        ]
        with open("output.json", "w+") as inp:
            json.dump(m, inp)
            inp.close()
        pass
