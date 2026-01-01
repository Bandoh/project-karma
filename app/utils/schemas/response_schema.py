response_schema = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "only visible if tool_call is False. so when no tool is needed put response here",
            },
            "reasoning": {
                "type": "string",
                "description": "Step-by-step execution plan. Strictly follow this format: 1. The user wants[fill in with users request] 2. How you are going to acheive it. NO conversational text allowed.",
            },
            "tool_call": {
                "type": "boolean",
                "description": "true or false depending on where you need a tool to fulfil request",
            },
            "tool": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "specify the specific tool_name I have provided you with",
                    },
                    "args": {
                        "type": "object",
                        "description": 'arguments needed for the tool it should be a map eg. {"command":"ls -la"}',
                        "additionalProperties": True,
                    },
                },
                "required": ["tool_name", "args"],
            },
        },
        "required": ["tool_call", "reasoning", "content"],
        "allOf": [
            {
                "if": {"properties": {"tool_call": {"const": True}}},
                "then": {"required": ["tool", "reasoning"]},
            },
            {
                "if": {"properties": {"tool_call": {"const": False}}},
                "then": {"required": ["content"]},
            },
        ],
    },
}
