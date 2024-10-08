from typing import Optional

from .base_config import BaseYAMLConfigModel


class BotConfig(BaseYAMLConfigModel):
    default_language: str
    last_n_messages_to_remember: int
    last_n_messages_to_store: Optional[int] = None
    default_usage_limit: int
