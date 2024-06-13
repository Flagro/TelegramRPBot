from .base_config import BaseYAMLConfigModel
from pydantic import BaseModel
from typing import Dict
import yaml


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
    
    @classmethod
    def load(self, file_path: str):
        with open(file_path, "r") as file:
            config_dict = yaml.safe_load(file)
            if "AIConfig" in config_dict:
                return AIConfig(**config_dict["AIConfig"])
            else:
                raise KeyError(f"AIConfig not found in {file_path}")        
