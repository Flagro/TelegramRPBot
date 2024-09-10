import tiktoken
import io
from typing import AsyncIterator, Literal
from openai import OpenAI
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ...models.config.ai_config import AIConfig, Model
from .agent_tools.describe_image import describe_image, ImageInformation


class AI:
    def __init__(self, openai_api_key: str, ai_config: AIConfig):
        self.ai_config = ai_config
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

    def _get_default_model_name(
        self, model_type: Literal["text", "vision", "image_generation"]
    ) -> str:
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
                return model.name
            if first_model is None:
                first_model = model.name
        return first_model

    def _get_default_text_model_name(self) -> str:
        return self._get_default_model_name("text")

    def _get_default_vision_model_name(self) -> str:
        return self._get_default_model_name("vision")

    def _get_default_image_generation_model_name(self) -> str:
        return self._get_default_model_name("image_generation")

    async def describe_image(
        self, in_memory_image_stream: io.BytesIO
    ) -> ImageInformation:
        # TODO: pass the image model into the chain
        return describe_image.invoke(in_memory_image_stream)

    async def transcribe_audio(self, in_memory_audio_stream: io.BytesIO) -> str:
        # TODO: implement this
        # r = await openai.Audio.atranscribe(in_memory_audio_stream)
        # return r["text"] or ""
        return ""

    async def generate_image(self, prompt: str):
        # TODO: implement this
        # r = await openai.Image.acreate(prompt=prompt, n=1, size="512x512")
        # image_url = r.data[0].url
        # return image_url
        return ""

    async def is_content_acceptable(self, text: str):
        # TODO: implement this
        # r = await openai.Moderation.acreate(input=text)
        # return not all(r.results[0].categories.values())
        return True

    @staticmethod
    def count_tokens(text: str):
        return tiktoken.count(text)

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]
        temperature = (self.ai_config.TextGeneration.temperature,)
        response = self.llm.ainvoke(messages, temperature=temperature)
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
