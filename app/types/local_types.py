from pydantic import BaseModel


class Config(BaseModel):
    model_name: str
    temperature: float
    system_message: str
