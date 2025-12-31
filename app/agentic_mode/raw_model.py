from app.utils.local_types import Config
from llama_cpp import Llama
import ast
import json
import multiprocessing
from app.utils.schemas.response_schema import response_schema
from app.utils.schemas.tools_schema import tools
from app.access.tools import terminal_access, search_anime
import re
class Agent:
    def __init__(self):
        self.conversation = []
        self.config = self.__load_config()
        self.conversation.append({"role":"system","content": (self.config.system_message.replace("[SCHEMA HERE]",str(response_schema).replace("'",'"')) ).replace("[TOOLS HERE]",str(tools))   })
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
        )
        pass
    def __load_config(self):
        with open(".config.json", "r") as inp:
            data = json.load(inp)
            local_data = Config(**data)
        return local_data
    
    def run(self,query,role):
        self.conversation.append({"role":role,"content":query})
        resp = self.llm.create_chat_completion(self.conversation)
        output = resp['choices'][0]['message']
        self.conversation.append(output)
        json_parsed_output = self.__handle_json(self.conversation[-1]['content'])
        if "tool_call" in json_parsed_output:
            if json_parsed_output['tool_call'] == "true" or json_parsed_output['tool_call'] ==True:
                tool_result = self.__handle_tool_selection(json_parsed_output['tool'])
                self.run("if user's request has been fullfilled set tool_call to false and remove tool key in json else set it to true if additional tool call is required and replace the content with resilt from the tool. This is the result: {}".format(tool_result),"tool")
        json_parsed_output = json.loads(self.conversation[-1]['content'])
        return json_parsed_output['content']
    
    def __handle_json(self,data:str):
        try:
            result = json.loads(data)
            return result
        except json.JSONDecodeError as e: 
            print("In Retry",data)
            print("Exception Message: ",e)
            self.run("format this:{} using this: {} use escape sequences for newline etc..".format(data,str(response_schema).replace("'",'"')),"system")


    def __handle_tool_selection(self,tool_info):
        print(tool_info)
        call = ""
        if tool_info['tool_name'] == "terminal_access":
            call = terminal_access(** tool_info['args'])
        if tool_info['tool_name'] == "search_anime":
            call = search_anime(** tool_info['args'])
        return call