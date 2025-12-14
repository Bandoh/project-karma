from langchain_ollama import ChatOllama
import json
from app.types.local_types import Config
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from app.tools.retrieval_tool import retrieve_context
from app.tools.update_memory import update_memory

config = {}

tools = [retrieve_context, update_memory]


def agent_run(query: str):
    with open(".config.json", "r") as inp:
        data = json.load(inp)
        config = Config(**data)

    llm = ChatOllama(model=config.model_name, temperature=config.temperature)
    personal_assistant_agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=config.system_message,
    )

    resp = personal_assistant_agent.invoke({"messages": [HumanMessage(query)]})

    # Check all messages for tool calls
    for message in resp["messages"]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            print(f"Tools used: {[tc['name'] for tc in message.tool_calls]}")

        # For AIMessage with tool_calls attribute
        if message.type == "ai" and hasattr(message, "tool_calls"):
            for tool_call in message.tool_calls:
                print(f"Tool: {tool_call['name']}, Args: {tool_call['args']}")

    print(resp["messages"][-1].content)
