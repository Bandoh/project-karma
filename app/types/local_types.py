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
