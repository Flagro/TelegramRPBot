from .base_config import BaseYAMLConfigModel
from typing import Dict
from pydantic import BaseModel


class ChatMode(BaseModel):
    name: str
    model_type: str = None
    welcome_message: str
    prompt_start: str
    parse_mode: str = None


class DefaultChatModes(BaseYAMLConfigModel):
    assistant: ChatMode
    motivator: ChatMode
