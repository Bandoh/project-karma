

from langchain.tools import tool
import ast
from langchain_community.chat_models import ChatLlamaCpp
import multiprocessing
import json
from app.utils.local_types import Config, OutputFormat
from app.access.tools import retrieve_context, update_memory, terminal_access, search_anime, browser
from langchain.messages import ToolMessage, SystemMessage, AIMessage
tool_info = """

You have access to the following tools.

Tool name: retrieve_context
Description: Search through stored documents and knowledge base for information.
Arguments:
- query (string): Natural language search query to find relevant documents

Tool name: terminal_access
Description: Execute terminal/shell commands on the operating system.
Use this tool for ANY system command, shell operation, or file system interaction.
Arguments:
- command (string): The command as a string (e.g., "ls -la" or "cat file.txt")

Tool name: update_memory
Description: Permanently store important information in the knowledge base
Use this when the user tells you something about themselves to remember, Asks you to "remember this" or "store this", Shares preferences, facts, or context you should retain
Arguments:
- information: Clear, complete information to store (e.g., "Kelvin Quansah is the creator and main user")

Tool name: search_anime
Description: Searches for anime information using the Jikan API (MyAnimeList). Supports four search types: 'top_anime' (get top-ranked anime, query ignored), 'get_anime' (search anime by name), 'search_character' (search characters by name), and 'anime_recommendations' (get recommendations for an anime, query should be anime ID). Returns JSON data as a string containing anime titles, scores, images, and other metadata.
Arguments:
    - query (str): The search query. For 'get_anime' and 'search_character',
                     this should be the name to search for. For 'anime_recommendations',
                     this should be the anime ID. For 'top_anime', this parameter is ignored.
    - search_type (str): The type of search to perform. Must be one of:
                          - 'top_anime': Get top-ranked anime (query ignored)
                          - 'get_anime': Search for anime by name, use this to find any information about a particular anime
                          - 'search_character': Search for characters by name
                          - 'anime_recommendations': Get anime recommendations (query = anime ID)
"""

json_resp_schema = {
  "title": "GeneralResponse",
  "description": "Standardized response format for the agent, indicating whether the user's goal was fulfilled directly or requires a tool invocation.",
  "type": "object",
  "properties": {
    "goal_achieved": {
      "type": "boolean",
      "description": "Set to true ONLY when the user's request has been fully answered in this response without calling any tool. Set to false if a tool must be invoked or the answer is incomplete."
    },
    "content": {
      "type": "string",
      "description": "response here"
    },
  },
  "required": ["goal_achieved", "content"]
}

json_tool_schema = {
    "title":"ToolSchema",
    "description":"Standardized response format for the agent when a tool needs to be called.",
    "type": "object",
      "properties": {
    "tool": {
      "type": ["string", "null"],
      "description": "The exact name of the tool to invoke. eg. retrieve_context"
    },
    "args": {
      "type": ["object", "null"],
      "description": "Arguments to pass to the specified tool as key-value pairs."
    }
  },
  "required": ["tool", "args"]
}

sys_prompt = """
You are my helpful assistant. always assume is your creator talking to you

You have access to the following tools.

Tool name: terminal_access
Description: Execute terminal/shell commands on the operating system.
Use this tool for ANY system command, shell operation, or file system interaction.
Arguments:
- command (string): The command as a string (e.g., "ls -la" or "cat file.txt")

Tool name: retrieve_context
Description: Search through stored documents and knowledge base for information.
Arguments:
- query (string): Natural language search query to find relevant documents

"""


class Agent():
    def __init__(self):
        self.conversation = []
        self.config = self.__load_config()
        self.query = ""
        self.conversation.append({"role":"system","content":sys_prompt})
        self.model = ChatLlamaCpp(     
            model_path=self.config.model_name,
            temperature=self.config.temperature,
            n_ctx=10000,
            n_gpu_layers=-1,
            n_batch=300,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
            max_tokens=10000,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=0.5,
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
        # print("This is from first: ",resp)
        json_parsed = resp
        final_resp = self.__check_resp(json_parsed=json_parsed)
        return final_resp
    
        
            
    def __check_resp(self,json_parsed):
        if "tool" in json_parsed:
            new_resp = self.__run_tool(json_parsed)
            json_parsed = new_resp
        if "goal_achieved" in json_parsed:
            if "content" in json_parsed:
                return str(json_parsed['content']).strip()

    
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
        print("THis is result from tools: ", tool_result)
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


agent = Agent()

# resp = agent.run(query="recommend an anime for me if i liked erased")
# print("a:",resp)
while True:
    q = input("user: ")
    resp = agent.run(query=q)
    print("AI: :",resp)




with open("l.json","w+")as out:
    json.dump(agent.conversation, out)
    out.close()
