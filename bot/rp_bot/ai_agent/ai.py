import tiktoken
import io
import base64
from typing import AsyncIterator, Literal, List
from openai import OpenAI
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from ..models.config.ai_config import AIConfig


class ImageInformation(BaseModel):
    # TODO: move this to prompt manager
    image_description: str = Field(description="a short description of the image")
    image_type: Literal["screenshot", "picture", "selfie", "anime"] = Field(description="type of the image")
    main_objects: List[str] = Field(description="list of the main objects on the picture")


class AI:
    def __init__(self, openai_api_key: str, ai_config: AIConfig):
        self.ai_config = ai_config
        self.llm = OpenAI(
            api_key=openai_api_key, model=self._get_default_text_model_name()
        )
        self.vision_model = OpenAI(
            api_key=openai_api_key, model="gpt-4-vision-preview" # TODO: add getter for vision model
        )

    def _get_default_text_model_name(self) -> str:
        first_model = None
        for model in self.ai_config.TextGeneration.Models.values():
            if model.is_default:
                return model.name
            if first_model is None:
                first_model = model.name
        return first_model

    async def describe_image(self, in_memory_image_stream: io.BytesIO) -> str:
        # Encode in base64:
        image_base64 = base64.b64encode(in_memory_image_stream.getvalue()).decode()
        parser = JsonOutputParser(pydantic_object=ImageInformation)
        
        # TODO: implement moderation
        # TODO: implement image chain runnable
        
        return ""

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
