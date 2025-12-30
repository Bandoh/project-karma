

from langchain.tools import tool
import ast
from langchain_community.chat_models import ChatLlamaCpp
import multiprocessing
import json
from app.utils.local_types import Config, json_resp_schema, json_tool_schema
from app.access.tools import retrieve_context, update_memory, terminal_access, search_anime, browser




class Agent():
    def __init__(self):
        self.conversation = []
        self.config = self.__load_config()
        self.query = ""
        self.tools = open("app/data/tools.txt","r").read()
        # if i liked erased what anime will you recommend
        self.conversation.append({"role":"system","content":self.config.system_message.replace("[TOOLS HERE]",self.tools)})
        self.model = ChatLlamaCpp(     
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

    def run(self,query):
        self.query = query
        self.conversation.append({"role":"user","content":self.query})
        resp = self.model.with_structured_output(json_tool_schema).invoke(self.conversation)
        print("This is from first: ",resp)
        json_parsed = resp
        final_resp = self.__check_resp(json_parsed=json_parsed)
        return final_resp
    
        
            
    def __check_resp(self,json_parsed):
        if "tool" in json_parsed:
            new_resp = self.__run_tool(json_parsed)
            json_parsed = new_resp
        if "goal_achieved" in json_parsed:
            if "content" in json_parsed:
                return json_parsed['content']

    
    def __run_tool(self,json_resp):
        tool_result = ""
        if json_resp['tool'] == "retrieve_context":
            tool_result = retrieve_context(**json_resp['args'])
        elif json_resp['tool'] == "terminal_access":
            tool_result = terminal_access(**json_resp['args'])
        elif json_resp['tool'] == "update_memory":
            tool_result = update_memory(**json_resp['args'])
        elif json_resp['tool'] == "search_anime":
            tool_result = search_anime(**json_resp['args'])
        # print("THis is result from tools: ", tool_result)
        self.conversation.append({
            "role": "tool",
            "content": str(tool_result),
            "tool_call_id": json_resp["tool"],
        })
        self.conversation.append({"role":"system","content":"The user asked {} so based on information from the tool Respond ".format(self.query)})
        new_resp = self.model.with_structured_output(json_resp_schema).invoke(self.conversation)
        self.conversation.append({"role":"assistant","content":new_resp.get("content", "")})
        return new_resp
    
    pass

