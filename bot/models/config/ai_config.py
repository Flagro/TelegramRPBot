from .base_config import BaseYAMLConfigModel
from pydantic import BaseModel
from typing import Dict


class Rate(BaseModel):
    input_token_price: int
    output_token_price: int


class Model(BaseModel):
    model_name: str
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
