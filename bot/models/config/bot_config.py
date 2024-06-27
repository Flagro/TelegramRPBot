from .base_config import BaseYAMLConfigModel


class BotConfig(BaseYAMLConfigModel):
    track_conversation_thread: bool
