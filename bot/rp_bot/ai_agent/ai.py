import tiktoken
import io
from typing import AsyncIterator, Literal, Optional
from openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ...models.config.ai_config import AIConfig, Model
from ...models.handlers_input import Message
from ..prompt_manager import PromptManager
from .agent_tools.describe_image import describe_image
from .agent_tools.check_engage_needed import check_engage_needed


class AI:
    def __init__(
        self, openai_api_key: str, ai_config: AIConfig, prompt_manager: PromptManager
    ):
        self.ai_config = ai_config
        self.prompt_manager = prompt_manager
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

    async def engage_is_needed(self, message: Message) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(
            message.message_text
        )
        return await check_engage_needed.ainvoke(self.llm, prompt)

    async def describe_image(self, in_memory_image_stream: io.BytesIO) -> str:
        # TODO: pass the image model into the chain
        image_information = await describe_image.ainvoke(in_memory_image_stream)
        image_description = await self.prompt_manager.compose_image_description_prompt(
            image_information
        )
        return image_description

    async def transcribe_audio(self, in_memory_audio_stream: io.BytesIO) -> str:
        # TODO: implement this
        # r = await openai.Audio.atranscribe(in_memory_audio_stream)
        # return r["text"] or ""
        return ""

    async def generate_image(self, prompt: str) -> str:
        """
        Returns the URL of the generated image
        """
        # TODO: implement this
        # r = await openai.Image.acreate(prompt=prompt, n=1, size="512x512")
        # image_url = r.data[0].url
        # return image_url
        return ""

    async def is_content_acceptable(self, text: str) -> bool:
        # TODO: implement this
        # r = await openai.Moderation.acreate(input=text)
        # return not all(r.results[0].categories.values())
        return True

    @staticmethod
    def count_tokens(text: str) -> int:
        return tiktoken.count(text)

    @staticmethod
    def compose_messages_langchain(user_input: str, system_prompt: str) -> list:
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]

    @staticmethod
    def compose_messages_openai(user_input: str, system_prompt: str) -> list:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        messages = self.compose_messages(user_input, system_prompt)
        temperature = (self.ai_config.TextGeneration.temperature,)
        response = await self.llm.ainvoke(messages, temperature=temperature)
        return response.content

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        messages = self.compose_messages_openai(user_input, system_prompt)
        temperature = (self.ai_config.TextGeneration.temperature,)
        for chunk in await self.llm.astream(messages, temperature=temperature):
            yield chunk.content
