from langchain_ollama import ChatOllama
import json
from app.types.local_types import Config, OutputFormat
from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from app.access.tools import retrieve_context, update_memory, terminal_access
from langchain.agents.structured_output import ToolStrategy


class Agent:
    def __init__(self):
        self.config = {}
        self.tools = {
            "retrieve_context": retrieve_context,
            "update_memory": update_memory,
            "terminal_access": terminal_access,
        }
        self.conversation = []
        self.llm = None
        self.initialized = False

    def run(self, query: str):
        if not self.initialized:
            self.llm = self._initialize()
            self.initialized = True

        self.conversation.append(HumanMessage(query))
        resp = self.llm.bind_tools(list(self.tools.values())).invoke(self.conversation)
        if resp.tool_calls:
            resp = self._handle_tools(resp)
        else:
            resp = self._handle_final_output()
        if resp.goal_achieved:
            return resp.content
        else:
            self.run(resp.content)

    def _initialize(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            self.config = Config(**data)
        llm = ChatOllama(
            model=self.config.model_name, temperature=self.config.temperature
        )
        self.conversation.append(SystemMessage(self.config.system_message))
        return llm

    def _handle_tools(self, response):
        print(response.tool_calls)
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id")

            print("Tool_name: {}, Tool_args: {}".format(tool_name, tool_args))
            tool_res = self.tools[tool_name].invoke(tool_call)
            self.conversation.append(
                ToolMessage(content=str(tool_res), tool_call_id=tool_id, name=tool_name)
            )
        return self._handle_final_output()

    def _handle_final_output(self):
        return self.llm.with_structured_output(OutputFormat).invoke(self.conversation)
