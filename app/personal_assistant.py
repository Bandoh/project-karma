from langchain_ollama import ChatOllama
import json
from app.types.local_types import Config, OutputFormat, output_format_schema
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from app.access.tools import retrieve_context, update_memory, terminal_access
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
import ast


class Agent:
    def __init__(self):
        self.config = {}
        self.tools = [
            retrieve_context,
            update_memory,
            terminal_access,
        ]
        self.conversation = []
        self.initialized = False
        self.personal_agent = ""

    def run(self, query: str):
        if not self.initialized:
            self._initialize()
            self.initialized = True

        self.conversation.append({"role": "user", "content": query})
        resp = self.personal_agent.invoke({"messages": self.conversation})
        self._list_tools_used(resp)
        parsed_resp = self._parse_structured_to_json(resp["messages"][-1].content)
        self.conversation.append(
            {
                "role": "ai",
                "content": str(parsed_resp),
            }
        )
        if parsed_resp["goal_achieved"]:
            print("Goal Acheived!")
        with open("output.json", "w+") as inp:
            json.dump(self.conversation, inp)
            inp.close()
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
        )

    def _list_tools_used(self, resp):
        for message in resp["messages"]:
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Tools used: {[tc['name'] for tc in message.tool_calls]}")

            # For AIMessage with tool_calls attribute
            if message.type == "ai" and hasattr(message, "tool_calls"):
                for tool_call in message.tool_calls:
                    print(f"Tool: {tool_call['name']}, Args: {tool_call['args']}")

    def _parse_structured_to_json(self, text: str):
        print("This is from parsing function ", text)
        json_str = text.replace("Returning structured response: ", "").strip()

        # Use ast.literal_eval to safely parse the Python dict string
        try:
            dict_obj = ast.literal_eval(json_str)
            return dict_obj
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing with ast.literal_eval: {e}")
            # Fallback: try direct json.loads in case it's already valid JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as je:
                print(f"Error parsing with json.loads: {je}")
                raise
