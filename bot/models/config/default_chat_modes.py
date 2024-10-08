from typing import Dict

from pydantic import BaseModel

from .base_config import BaseYAMLConfigModel


class ChatMode(BaseModel):
    name: str
    description: str


class DefaultChatModes(BaseYAMLConfigModel):
    default_chat_modes: Dict[str, ChatMode]
