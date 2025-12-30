from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatLlamaCpp
import json
from app.utils.local_types import Config, output_format_schema
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AnyMessage
from app.access.tools import (
    retrieve_context,
    update_memory,
    terminal_access,
    browser,
    search_anime,
)
import multiprocessing
from langchain.agents.structured_output import ToolStrategy
from app.utils.memory_management import MemoryManager, KarmaAgentState
import ast


class Agent:
    def __init__(self, memory_manager: MemoryManager):
        self.config = {}
        self.memory_manager = memory_manager
        self.tools = [
            retrieve_context,
            update_memory,
            terminal_access,
            browser,
            search_anime,
        ]
        self.memory_config = {"configurable": {"thread_id": "1"}}
        self.initialized = False
        self.personal_agent = ""

    def run(self, query: str):
        if not self.initialized:
            self._initialize()
            self.initialized = True
        resp = self.personal_agent.invoke(
            {"messages": [HumanMessage(query)], "user_name": "Kelvin Gander"},
            self.memory_config,
        )
        print(resp)
        self._list_tools_used(resp)
        last_response = self._save_chat_history(
            self.personal_agent.get_state(self.memory_config).values["messages"]
        )
        return self._parse_structured_response(last_response)["content"]

    def _initialize(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            self.config = Config(**data)
        custom_profile = {
            "structured_output": True,
            # ...
        }
        print("About to Initialize Model")
        llm = ChatLlamaCpp(    
            model_path=self.config.model_name,
            temperature=self.config.temperature,
            profile=custom_profile,
            n_ctx=10000,
            n_gpu_layers=10000,
            n_batch=300,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
            max_tokens=512,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=0.5,
            verbose=True,
        )
        self.personal_agent = create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=self.config.system_message,
            # response_format=ToolStrategy(output_format_schema),
            checkpointer=self.memory_manager.get_checkpointer(),
            state_schema=KarmaAgentState,
        )

    def _list_tools_used(self, resp):
        tool_used = False
        for message in resp["messages"]:
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Tools used: {[tc['name'] for tc in message.tool_calls]}")
                tool_used = True
            # For AIMessage with tool_calls attribute
            if message.type == "ai" and hasattr(message, "tool_calls"):
                for tool_call in message.tool_calls:
                    print(f"Tool: {tool_call['name']}, Args: {tool_call['args']}")
                    tool_used = True
        return tool_used

    def _save_chat_history(self, messages: list[AnyMessage]):
        last_message = ""
        m = [
            {"role": message.type, "content": message.content}
            for message in messages
            if message.content
        ]
        last_message = m[-1]["content"]
        with open("output.json", "w+") as inp:
            json.dump(m, inp)
            inp.close()
        return last_message

    def _parse_structured_response(self, response_string: str) -> dict:
        """
        Parse structured response from a string.

        Args:
            response_string: String like "Returning structured response: {'content': '...', 'goal_achieved': 'true'}"

        Returns:
            Dictionary with parsed content
        """
        try:
            # Remove the prefix "Returning structured response: "
            if "Returning structured response: " in response_string:
                dict_string = response_string.split(
                    "Returning structured response: ", 1
                )[1]
            else:
                print("Not using STRUCTURED RESPONSE")
                dict_string = response_string

            # Parse the dictionary string
            parsed_dict = ast.literal_eval(dict_string)
            return parsed_dict
        except:
            return {"content": dict_string, "goal_acheived": True}
