from app.utils.local_types import Config
from llama_cpp import Llama
import ast
import json5
import multiprocessing
from app.utils.schemas.response_schema import response_schema
from app.utils.schemas.tools_schema import tools
from app.access.tools import terminal_access, search_anime, retrieve_context
import re
import json
from app.utils.loger_config import get_logger

logger = get_logger(__name__)


class Agent:
    def __init__(self):
        self.conversation = []
        self.config = self.__load_config()
        self.conversation.append(
            {
                "role": "system",
                "content": (
                    self.config.system_message.replace(
                        "[SCHEMA HERE]", str(response_schema).replace("'", '"')
                    )
                ).replace("[TOOLS HERE]", str(tools)),
            }
        )
        self.query = ""
        self.llm = Llama(
            model_path=self.config.model_name,
            temperature=self.config.temperature,
            n_ctx=20000,
            n_gpu_layers=-1,
            n_batch=300,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
            max_tokens=10000,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.1,
            top_p=0.95,
            verbose=False,
        )
        pass

    def __load_config(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            local_data = Config(**data)
        return local_data

    def run(self, query, role):
        self.conversation.append({"role": role, "content": query})

        # Use iteration instead of recursion
        while True:
            resp = self.llm.create_chat_completion(
                self.conversation, response_format=response_schema
            )
            output = resp["choices"][0]["message"]
            json_parsed_output = self.__safe_json_parse(output["content"])

            # Check if tool call is needed
            needs_tool_call = json_parsed_output.get("tool_call") in ("true", True)

            if needs_tool_call:
                # Remove content, keep reasoning
                del json_parsed_output["content"]
                self.conversation.append(
                    {"role": "assistant", "content": json_parsed_output}
                )

                # Execute tool
                tool_result = self.__handle_tool_selection(json_parsed_output["tool"])

                # Add tool result to conversation
                self.conversation.append(
                    {
                        "role": "user",
                        "content": f"Strictly use this information to answer the question: {tool_result}. Set tool_call to False if request is fulfilled else set to True with respective args",
                    }
                )
                # Loop continues for next LLM call
            else:
                # Final response
                del json_parsed_output["reasoning"]
                self.conversation.append(
                    {"role": "assistant", "content": json_parsed_output}
                )
                return json_parsed_output["content"]

    def __safe_json_parse(self, raw_content):
        """
        Attempt to parse LLM output as JSON5.
        If parsing fails, wrap content in a dict to avoid type errors.
        """
        try:
            # Escape problematic newlines
            escaped_content = raw_content.replace("\n", "\\n").replace("\r", "")
            parsed = json5.loads(escaped_content)
            # If the model outputs plain string, wrap it
            if isinstance(parsed, str):
                return {"content": parsed}
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}\nContent was: {raw_content}")
            # Fallback: always return a dict
            return {"content": raw_content}

    def __handle_tool_selection(self, tool_info):
        call = ""
        if tool_info["tool_name"] == "terminal_access":
            call = terminal_access(**tool_info["args"])
        if tool_info["tool_name"] == "search_anime":
            call = search_anime(**tool_info["args"])
        if tool_info["tool_name"] == "retrieve_context":
            call = retrieve_context(**tool_info["args"])
        return call
