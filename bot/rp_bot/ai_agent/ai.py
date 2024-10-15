import tiktoken
import io
from typing import AsyncIterator, Literal, Optional
from openai import OpenAI
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ...models.config.ai_config import AIConfig, Model
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
            api_key=openai_api_key, model=self._get_default_text_model_name()
        )
        self.vision_model = OpenAI(
            api_key=openai_api_key,
            model=self._get_default_vision_model_name(),
        )
        # TODO: fix this - this is not OpenAI object
        self.image_generation_model = OpenAI(
            api_key=openai_api_key,
            model=self._get_default_image_generation_model_name(),
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

    def _get_model_by_name(
        self, model_name: str, model_type: Literal["text", "vision", "image_generation"]
    ) -> Model:
        models_dict = {
            "text": self.ai_config.TextGeneration.Models,
            "vision": self.ai_config.TextGeneration.Models,
            "image_generation": self.ai_config.ImageGeneration.Models,
        }
        return models_dict[model_type].get(model_name)

    def _get_default_text_model_name(self) -> str:
        return self._get_default_model("text").name

    def _get_default_vision_model_name(self) -> str:
        return self._get_default_model("vision").name

    def _get_default_image_generation_model_name(self) -> str:
        return self._get_default_model("image_generation").name

    def get_price(
        self, token_len: int, audio_length: int, image_pixels_count: int
    ) -> float:
        """
        Returns the price of the AI services for the given
        input parameters
        
        Args:
        token_len: the number of tokens in the input text
        audio_length: the length of the audio in seconds
        image_pixels_count: the number of pixels in the image
        """
        # TODO: take rates by model name
        input_token_price = self.ai_config.TextGeneration.rate.input_token_price
        output_token_price = self.ai_config.TextGeneration.rate.output_token_price
        input_pixel_price = self.ai_config.TextGeneration.rate.input_pixel_price
        output_pixel_price = self.ai_config.TextGeneration.rate.output_pixel_price
        return (
            token_len * input_token_price
            + token_len * output_token_price
            + audio_length * input_token_price
            + image_pixels_count * input_pixel_price
            + image_pixels_count * output_pixel_price
        )

    async def engage_is_needed(self, user_input: str) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(user_input)
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

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]
        temperature = (self.ai_config.TextGeneration.temperature,)
        response = await self.llm.ainvoke(messages, temperature=temperature)
        return response.content

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]
        temperature = (self.ai_config.TextGeneration.temperature,)
        for chunk in await self.llm.astream(messages, temperature=temperature):
            yield chunk.content
