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
        },
    },
}

anime_search_tool = {
    "type": "function",
    "function": {
        "name": "search_anime",
        "description": "Anything related to anime use this tool. It Searches anime data using the Jikan API (MyAnimeList).\n\nINTENT RULES (MANDATORY):\n- If the user asks for recommendations, similar anime, what to watch next, or says phrases like 'recommend', 'similar to', 'if I liked X', you MUST use search_type = 'anime_recommendations'.\n- Using 'get_anime' for recommendations is INVALID and must NEVER happen.\n- 'get_anime' is ONLY for factual information such as synopsis, episodes, release date, or studio.\n- 'top_anime' is ONLY for ranking queries.\n- 'search_character' is ONLY for character lookups.",
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
                    "description": "Type of search to perform",
                },
            },
            "required": ["search_type"],
        },
    },
}

retrieve_context_tool = {
    "type": "function",
    "function": {
        "name": "retrieve_context",
        "description": "Retrieves relevant information from your memory/knowledge base..whenever youre unsure of something use this tool first",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query describing what information to find. Be specific. Examples: 'user preferences for coding style', 'previous conversation about project X', 'information about user's background in Python'",
                }
            },
            "required": ["query"],
        },
    },
}
tools = [terminal_access_tool, retrieve_context_tool, anime_search_tool]
