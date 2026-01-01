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
                "content": (self.config.system_message),
            }
        )
        self.query = ""
        self.llm = Llama(
            model_path=self.config.model_name,
            n_ctx=20000,
            n_gpu_layers=-1,
            n_batch=300,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
            max_tokens=10000,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.1,
            top_p=0.95,
            verbose=False,
            chat_format="chatml-function-calling",
        )
        pass

    def __load_config(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            local_data = Config(**data)
        return local_data

    def run(self, query, role="user"):
        self.conversation.append({"role": role, "content": query})

        resp = self.llm.create_chat_completion(
            self.conversation,
            tools=tools,
            tool_choice="auto",
        )

        msg = resp["choices"][0]["message"]

        if msg.get("tool_calls"):
            tool_call = msg["tool_calls"][0]
            tool_info = tool_call["function"]

            tool_result = self.__handle_tool_selection(tool_info)

            # self.conversation.append(
            #     {
            #         "role": "assistant",
            #         "tool_call_id": tool_call["id"],
            #         "content": json.dumps(tool_result),
            #     }
            # )
            self.conversation.append(
                {
                    "role": "user",
                    "content": f"use the answer from here:{tool_result}  to answer my question question",
                }
            )
            final_resp = self.llm.create_chat_completion(self.conversation)
            final_msg = final_resp["choices"][0]["message"]
            self.conversation.append(final_msg)
            return final_msg["content"]
        final_resp = self.llm.create_chat_completion(self.conversation, temperature=0.7)
        self.conversation.append(final_resp["choices"][0]["message"])
        return final_resp["choices"][0]["message"]["content"]

    def __handle_tool_selection(self, tool_info):
        logger.info(tool_info)
        function_args = json.loads(tool_info["arguments"])
        call = ""
        if tool_info["name"] == "terminal_access":
            call = terminal_access(**function_args)
        if tool_info["name"] == "search_anime":
            call = search_anime(**function_args)
        if tool_info["name"] == "retrieve_context":
            call = retrieve_context(**function_args)
        return call
