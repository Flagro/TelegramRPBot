import tiktoken
import io
from typing import AsyncIterator, Literal, Optional, List, Dict, Any
from openai import OpenAI

from ...models.config.ai_config import AIConfig, Model
from ...models.handlers_input import Message, Person, Context
from ...models.base_moderation import ModerationError
from ..prompt_manager import PromptManager
from .ai_utils.describe_image import describe_image
from .moderation import Moderation
from .agent_tools.agent_toolkit import AIAgentToolkit


class AI:
    def __init__(
        self, openai_api_key: str, ai_config: AIConfig, prompt_manager: PromptManager
    ):
        moderation_model = OpenAI(api_key=openai_api_key)
        self.moderation = Moderation(model=moderation_model)
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

    async def engage_is_needed(
        self, person: Person, context: Context, message: Message
    ) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(
            message.message_text
        )
        # TODO: we should pass the OpenAI toolkit with all the models
        toolkit = AIAgentToolkit(person, context, message, self.llm)
        return await toolkit.check_engage_needed.run(prompt)

    async def describe_image(self, in_memory_image_stream: io.BytesIO) -> str:
        if not self.moderation.moderate_image(in_memory_image_stream):
            raise ModerationError("Image is not safe")
        # TODO: pass the image model into the chain
        image_information = await describe_image(in_memory_image_stream)
        image_description = await self.prompt_manager.compose_image_description_prompt(
            image_information
        )
        return image_description

    async def transcribe_audio(self, in_memory_audio_stream: io.BytesIO) -> str:
        if not self.moderation.moderate_audio(in_memory_audio_stream):
            raise ModerationError("Audio is not safe")
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

    @staticmethod
    def count_tokens(text: str) -> int:
        return tiktoken.count(text)

    @staticmethod
    def compose_messages_openai(user_input: str, system_prompt: str) -> list:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

    def create_response(
        self, messages: List[Dict[str, str]], stream: bool = False
    ) -> Any:
        # TODO: Fix Any return type
        return self.llm.chat.completions.create(
            model=self._get_default_model("text").name,
            messages=messages,
            stream=stream,
            temperature=self.ai_config.TextGeneration.temperature,
        )

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.compose_messages_openai(user_input, system_prompt)
        response = self.create_response(messages)
        return response.choices[0].message.content

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.compose_messages_openai(user_input, system_prompt)
        response = self.create_response(messages, stream=True)
        for chunk in response:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
