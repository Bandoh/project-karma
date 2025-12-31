terminal_access_tool = {
  "type": "function",
  "function": {
    "name": "terminal_access",
    "description": "Executes terminal or shell commands on the operating system. Use this tool when the user's intent is to obtain information or perform actions that REQUIRE access to the operating system, file system, or runtime environment. This includes: inspecting the file system (what files exist, file contents, permissions), executing commands or scripts, inspecting system state (OS, CPU, memory, disk, processes), debugging issues that require real command output, and running or testing programs. DO NOT use this tool for: learning how to use a command (explanation only), asking what would happen if a command is run, theoretical or conceptual questions, or requesting reasoning, advice, or summaries. CRITICAL: Any request involving files, folders, directories, paths, listing, reading, writing, or system state MUST use this tool.",
    "parameters": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "description": "The exact shell command to execute on the operating system"
        }
      },
      "required": ["command"],
      "additionalProperties": False
    },
    "strict": True
  }
}

anime_search_tool = {
  "name": "search_anime",
  "description": "Searches anime data using the Jikan API (MyAnimeList).\n\nINTENT RULES (MANDATORY):\n- If the user asks for recommendations, similar anime, what to watch next, or says phrases like 'recommend', 'similar to', 'if I liked X', you MUST use search_type = 'anime_recommendations'.\n- Using 'get_anime' for recommendations is INVALID and must NEVER happen.\n- 'get_anime' is ONLY for factual information such as synopsis, episodes, release date, or studio.\n- 'top_anime' is ONLY for ranking queries.\n- 'search_character' is ONLY for character lookups.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Anime or character name. Required for all search types except 'top_anime'."
      },
      "search_type": {
        "type": "string",
        "enum": [
          "anime_recommendations",
          "get_anime",
          "top_anime",
          "search_character"
        ]
      }
    },
    "required": ["search_type"]
  }
}

retreive_context_tool =   {
    "name": "retrieve_context",
    "description": "this is your internal memory now before you anser anything use this tool first",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "A natural-language query describing what information to retrieve from stored context."
        }
      },
      "required": ["query"]
    }
  }




tools = [terminal_access_tool, anime_search_tool, retreive_context_tool]
