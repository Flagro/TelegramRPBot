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

    def get_price(
        self,
        token_len: int,
        audio_length: int,
        image_pixels_count: int,
        image_generation_needed: bool,
    ) -> float:
        """
        Returns the price of the AI services for the given
        input parameters

        Args:
        token_len: the number of tokens in the input text
        audio_length: the length of the audio in seconds
        image_pixels_count: the number of pixels in the image
        """
        input_token_price = self._get_default_model("text").rate.input_token_price
        output_token_price = self._get_default_model("text").rate.output_token_price
        input_pixel_price = self._get_default_model("vision").rate.input_pixel_price
        output_pixel_price = self._get_default_model(
            "image_generation"
        ).rate.output_pixel_price

        image_generation_dimensions = self.ai_config.ImageGeneration.output_image_size
        image_generation_dimensions_x, image_generation_dimensions_y = (
            image_generation_dimensions.split("x")
        )
        image_generation_pixels = (
            0
            if not image_generation_needed
            else int(image_generation_dimensions_x) * int(image_generation_dimensions_y)
        )

        return (
            token_len * input_token_price
            + token_len * output_token_price
            + audio_length * input_token_price
            + image_pixels_count * input_pixel_price
            + image_generation_pixels * output_pixel_price
        )
