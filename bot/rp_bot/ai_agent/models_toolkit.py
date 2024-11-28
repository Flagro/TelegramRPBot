from typing import Literal, Optional
from openai import OpenAI

from ...models.config.ai_config import AIConfig, Model


class ModelsToolkit:
    def __init__(self, openai_api_key: str, ai_config: AIConfig):
        self.ai_config = ai_config
        llm = OpenAI(api_key=openai_api_key, model=self._get_default_model("text").name)
        vision_model = OpenAI(
            api_key=openai_api_key,
            model=self._get_default_model("vision").name,
        )
        # TODO: fix this - this is not OpenAI object
        image_generation_model = OpenAI(
            api_key=openai_api_key,
            model=self._get_default_model("image_generation").name,
        )

    def _get_default_model(
        self, model_type: Literal["text", "vision", "image_generation"]
    ) -> Optional[Model]:
        params_dict = {
            "text": {
                "models_dict": self.ai_config.TextGeneration.Models,
                "default_attr": "text_default",
            },
            "vision": {
                "models_dict": self.ai_config.TextGeneration.Models,
                "default_attr": "vision_default",
            },
            "image_generation": {
                "models_dict": self.ai_config.ImageGeneration.Models,
                "default_attr": "image_generation_default",
            },
        }
        first_model = None
        for model in params_dict[model_type]["models_dict"].values():
            if getattr(model, params_dict[model_type]["default_attr"]):
                return model
            if first_model is None:
                first_model = model
        return first_model
