from .base_config import BaseYAMLConfigModel
from pydantic import BaseModel
from typing import Dict, Optional


class Rate(BaseModel):
    input_token_price: int
    output_token_price: int


class Model(BaseModel):
    name: str
    is_default: Optional[bool] = False
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
