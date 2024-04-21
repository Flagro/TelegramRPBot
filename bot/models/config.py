from pydantic import BaseModel, Field
from typing import Dict
import yaml


class BaseYAMLConfigModel(BaseModel):
    """Base model with a load method for loading from a yaml file."""

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
            if cls.__name__ in config_dict:
                return cls(**config_dict[cls.__name__])
            else:
                raise KeyError(f"{cls.__name__} not found in {file_path}")


class TGConfig(BaseYAMLConfigModel):
    new_dialog_timeout: int
    enable_message_streaming: bool
    n_chat_modes_per_page: int
    track_conversation_thread: bool


class DefaultChatModes(BaseYAMLConfigModel):
    name: str
    model_type: str
    welcome_message: str
    prompt_start: str
    parse_mode: str


class LocalizerTranslation(BaseModel):
    english: str = Field(..., alias='english')

    class Config:
        allow_population_by_field_name = True

class LocalizerTranslations(BaseYAMLConfigModel):
    translations: Dict[str, LocalizerTranslation]


class DBConfig(BaseYAMLConfigModel):
    DB_SCHEME: str
    DB_HOST: str
    DB_PORT: int


class Rate(BaseModel):
    input_token_price: int
    output_token_price: int


class Model(BaseModel):
    rate: Rate


class TextGeneration(BaseModel):
    temperature: float
    max_tokens: int
    top_p: int
    frequency_penalty: int
    presence_penalty: int
    request_timeout: float
    Models: Dict[str, Model]


class ImageProcessing(BaseModel):
    image_size: str


class AIConfig(BaseYAMLConfigModel):
    TextGeneration: TextGeneration
    ImageProcessing: ImageProcessing


class AuthConfig(BaseModel):
    allowed_handles: str
    admin_handles: str
