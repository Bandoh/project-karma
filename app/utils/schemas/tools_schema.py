terminal_access_tool = {
    "type": "function",
    "function": {
        "name": "terminal_access",
        "description": "Executes shell commands on the operating system. Use this to: list/read/write files and directories, run programs or scripts, check system information (OS, CPU, memory, processes), inspect file system state, or perform any action requiring command-line access.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute (e.g., 'ls -la', 'cat file.txt', 'python script.py')",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

anime_search_tool = {
    "name": "search_anime",
    "description": "Searches anime data using the Jikan API (MyAnimeList).\n\nINTENT RULES (MANDATORY):\n- If the user asks for recommendations, similar anime, what to watch next, or says phrases like 'recommend', 'similar to', 'if I liked X', you MUST use search_type = 'anime_recommendations'.\n- Using 'get_anime' for recommendations is INVALID and must NEVER happen.\n- 'get_anime' is ONLY for factual information such as synopsis, episodes, release date, or studio.\n- 'top_anime' is ONLY for ranking queries.\n- 'search_character' is ONLY for character lookups.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Anime or character name. Required for all search types except 'top_anime'.",
            },
            "search_type": {
                "type": "string",
                "enum": [
                    "anime_recommendations",
                    "get_anime",
                    "top_anime",
                    "search_character",
                ],
            },
        },
        "required": ["search_type"],
    },
}

retrieve_context_tool = {
    "name": "retrieve_context",
    "description": """Retrieves relevant information from your memory/knowledge base. 

CRITICAL: You MUST call this tool BEFORE answering any user question to check if relevant context exists.

This tool searches through previously stored conversations, documents, and context to find information relevant to the current query. Always retrieve context first, then use that information to provide accurate, personalized responses.

Examples of when to use:
- User asks a question → retrieve context about that topic first
- User references previous conversation → retrieve that conversation
- User asks about their preferences → retrieve their stored preferences
- Any query that might benefit from historical context → retrieve first

Call this at the START of your response, not after attempting to answer.""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query describing what information to find. Be specific. Examples: 'user preferences for coding style', 'previous conversation about project X', 'information about user's background in Python'",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}

tools = [terminal_access_tool, anime_search_tool, retrieve_context_tool]
