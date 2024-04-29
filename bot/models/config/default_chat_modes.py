from .base_config import BaseYAMLConfigModel


class DefaultChatModes(BaseYAMLConfigModel):
    name: str
    model_type: str
    welcome_message: str
    prompt_start: str
    parse_mode: str
