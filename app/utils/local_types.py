from pydantic import BaseModel, Field


class Config(BaseModel):
    model_name: str
    temperature: float
    system_message: str


class OutputFormat(BaseModel):
    """Schema for agent response output."""

    goal_achieved: bool = Field(
        description="Whether the user's goal or request was successfully achieved"
    )
    content: str = Field(description="The response content to display to the user")


output_format_schema = {
    "type": "object",
    "description": "Schema for agent response output.",
    "properties": {
        "goal_achieved": {
            "type": "boolean",
            "description": "Whether the user's goal or request was successfully achieved. For pleasantries like Hi, Hello etc... goal is always achieved in response",
        },
        "content": {
            "type": "string",
            "description": "The response content to display to the user",
        },
    },
    "required": ["goal_achieved", "content"],
}

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
