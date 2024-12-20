from .base_config import BaseYAMLConfigModel


class TGConfig(BaseYAMLConfigModel):
    new_dialog_timeout: int
    enable_message_streaming: bool
    n_chat_modes_per_page: int
    stream_buffer_sleep_time: float
    rate_limiter_max_retries: int
