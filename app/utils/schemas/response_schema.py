response_schema = {
    "content": " if tool is needed tell me the steps If no tool is needed put response here",
    "tool_call": "true or false depending on where you need a tool to fulfil request",
    "tool (this shows only if tool_call is true)": {
        "tool_name": "specify the specific tool_name i have provided you with",
        "args": """arguements needed for the tool it should be a map eg. {"command":"ls -la"}""",
    },
}
response_schema = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Response text if no tool is needed",
            },
            "tool_call": {
                "type": "boolean",
                "description": "True if a tool is required, false otherwise",
            },
            "tool": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "args": {
                        "type": "object",
                        "additionalProperties": True,
                    },
                },
                "required": ["tool_name", "args"],
            },
        },
        "required": ["content", "tool_call"],
        "if": {"properties": {"tool_call": {"const": True}}},
        "then": {"required": ["tool"]},
    },
}
