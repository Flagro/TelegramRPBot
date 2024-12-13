from typing import Literal, Optional, AsyncGenerator, List, Dict
from openai import OpenAI
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from ...models.config.ai_config import AIConfig, Model


class YesOrNoInvalidResponse(Exception):
    pass


class ModelsToolkit:
    def __init__(self, openai_api_key: str, ai_config: AIConfig):
        self.ai_config = ai_config
        self.llm = OpenAI(
            api_key=openai_api_key, model=self._get_default_model("text").name
        )
        self.vision_model = OpenAI(
            api_key=openai_api_key,
            model=self._get_default_model("vision").name,
        )
        # TODO: fix this - this is not OpenAI object
        self.image_generation_model = OpenAI(
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
        image_generation_needed: whether the image generation is needed
        """
        input_token_price = self._get_default_model("text").rate.input_token_price
        output_token_price = self._get_default_model("text").rate.output_token_price
        input_pixel_price = self._get_default_model("vision").rate.input_pixel_price
        output_pixel_price = self._get_default_model(
            "image_generation"
        ).rate.output_pixel_price

        image_generation_dimensions = self.ai_config.ImageGeneration.output_image_size
        if "x" not in image_generation_dimensions:
            raise ValueError(
                f"Invalid image generation dimensions: {image_generation_dimensions}"
            )
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

    @staticmethod
    def compose_message_openai(
        message_text: str, role: Literal["user", "system"] = "user"
    ) -> List[Dict[str, str]]:
        return [{"role": role, "content": message_text}]

    def get_default_temperature(self) -> float:
        return self.ai_config.TextGeneration.temperature

    @staticmethod
    def compose_messages_openai(
        user_input: str, system_prompt: str
    ) -> List[Dict[str, str]]:
        return ModelsToolkit.compose_message_openai(
            system_prompt, role="system"
        ) + ModelsToolkit.compose_message_openai(user_input, role="user")

    async def get_response(self, messages: List[Dict[str, str]]) -> str:
        response = self.llm.chat.completions.create(
            model=self._get_default_model("text").name,
            messages=messages,
            stream=False,
            temperature=self.get_default_temperature(),
        )
        text_response = response.choices[0].message.content
        return text_response

    async def get_streaming_response(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str]:
        response = self.llm.chat.completions.create(
            model=self._get_default_model("text").name,
            messages=messages,
            stream=True,
            temperature=self.get_default_temperature(),
        )
        async for message in response:
            yield message.choices[0].message.content

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(YesOrNoInvalidResponse),
    )
    async def ask_yes_no_question(self, question: str) -> bool:
        text_response = await self.get_response(self.compose_message_openai(question))
        lower_response = text_response.lower()
        if "yes" in lower_response:
            return True
        if "no" in lower_response:
            return False
        raise YesOrNoInvalidResponse(f"Response: {text_response}")
