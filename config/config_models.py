from pydantic import BaseModel, Field
from typing import Dict
import yaml


class TGConfig(BaseModel):
    new_dialog_timeout: int
    enable_message_streaming: bool
    n_chat_modes_per_page: int
    track_conversation_thread: bool
    
    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict['TG'])


class ChatMode(BaseModel):
    name: str
    model_type: str
    welcome_message: str
    prompt_start: str
    parse_mode: str

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict['DefaultChatModes'])


class Translation(BaseModel):
    english: str = Field(..., alias='english')

    class Config:
        allow_population_by_field_name = True

class Translations(BaseModel):
    translations: Dict[str, Translation]

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(translations=config_dict['Translations'])


class DBConfig(BaseModel):
    DB_SCHEME: str
    DB_HOST: str
    DB_PORT: int

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict['DB'])


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


class AIConfig(BaseModel):
    TextGeneration: TextGeneration
    ImageProcessing: ImageProcessing

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict['AI'])
