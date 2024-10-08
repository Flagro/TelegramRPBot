from typing import Dict, Optional

from pydantic import BaseModel

from .base_config import BaseYAMLConfigModel


class Rate(BaseModel):
    input_token_price: Optional[float]
    output_token_price: Optional[float]
    input_pixel_price: Optional[float]
    output_pixel_price: Optional[float]


class Model(BaseModel):
    name: str
    text_default: Optional[bool] = False
    vision_default: Optional[bool] = False
    image_generation_default: Optional[bool] = False
    rate: Rate


class TextGeneration(BaseModel):
    temperature: float
    max_tokens: int
    top_p: int
    frequency_penalty: int
    presence_penalty: int
    request_timeout: float
    Models: Dict[str, Model]


class ImageGeneration(BaseModel):
    output_image_size: str
    request_timeout: float
    Models: Dict[str, Model]


class AIConfig(BaseYAMLConfigModel):
    TextGeneration: TextGeneration
    ImageGeneration: ImageGeneration
