from .base_config import BaseYAMLConfigModel


class BotConfig(BaseYAMLConfigModel):
    default_language: str
    last_n_messages_to_remember: int
    default_usage_limit: int
