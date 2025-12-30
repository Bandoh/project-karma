

from langchain.tools import tool
import ast
from langchain_community.chat_models import ChatLlamaCpp
import multiprocessing
import json
from app.utils.local_types import Config, OutputFormat
from app.access.tools import retrieve_context, update_memory, terminal_access, search_anime, browser
from pydantic import BaseModel, Field

json_resp_schema = {
  "title": "GeneralResponse",
  "description": "A response indicating whether a goal was achieved with content",
  "type": "object",
  "properties": {
    "goal_achieved": {
      "type": "boolean",
      "description": "answered based on where the previous question has been answered"
    },
    "content": {
      "type": "string",
      "description": "actual response here"
    },
    "tool": {
      "type": ["string", "null"],
      "description": "name of the tool to use, or null if no tool is needed"
    },
    "args": {
      "type": ["object", "null"],
      "description": "arguments for the tool as key-value pairs, or null if no tool is needed"
    }
  },
  "required": ["goal_achieved", "content", "tool", "args"]
}

sys_prompt = """
You are my helpful assistant. always assume is your creator talking to you

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

RULES:
- If a tool is needed, respond ONLY with valid JSON
- Format:
  {"tool": "<tool_name>", "args": {...}}
- No extra text
"""


class Agent():
    def __init__(self):
        self.conversation = []
        self.config = self.__load_config()
        self.conversation.append(("system",sys_prompt))
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
        self.conversation.append(("human",query))
        resp = self.model.invoke(self.conversation)
        print("This is from first: ",resp)
        json_parsed = json.loads(self.__clean_json(resp.content))
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
        self.conversation.append(("assistant",tool_result))
        self.conversation.append(("system","The tool has been executed. Respond now with the FINAL answer using {'goal_achieved':true|false(strictly answered based on where the previous question has been answered), 'content':'response here'} format only."))
        new_resp = self.model.with_structured_output(json_resp_schema).invoke(self.conversation)
        print("This is from pydantic",new_resp)
        return new_resp
    
    def __clean_json(self, resp: str) -> str:
        """
        Safely cleans a string to be valid JSON.
        - Escapes inner quotes
        - Removes invalid characters
        """
        # Remove invalid escape sequences
        resp = resp.replace('\m', '')  

        # If single quotes are used for keys/values, try converting safely
        if resp.startswith("{") and resp.endswith("}"):
            try:
                # Try parsing with ast.literal_eval and then dump as proper JSON
                parsed = ast.literal_eval(resp)
                resp = json.dumps(parsed)
            except Exception:
                print("In Exception!!")
                # fallback: just escape internal double quotes
                resp = resp.replace('"', '\\"')
                resp = f'"{resp}"'
        return resp
    pass


agent = Agent()

resp = agent.run(query="recommend an anime for me if i liked erased")
print("a:",resp)
resp = agent.run(query="where did Kelvin Quansah go to school")
print("a:",resp)
