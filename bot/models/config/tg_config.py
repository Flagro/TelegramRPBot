from .base_config import BaseYAMLConfigModel


class TGConfig(BaseYAMLConfigModel):
    new_dialog_timeout: int
    enable_message_streaming: bool
    n_chat_modes_per_page: int
    track_conversation_thread: bool
