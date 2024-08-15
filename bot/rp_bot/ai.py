import tiktoken
import io
from typing import AsyncIterator
from openai import OpenAI

from .db import DB
from ..models.config.ai_config import AIConfig


def count_tokens(text: str):
    return tiktoken.count(text)


async def is_content_acceptable(text: str):
    # TODO: implement this
    # r = await openai.Moderation.acreate(input=text)
    # return not all(r.results[0].categories.values())
    return True


class AI:
    def __init__(self, openai_api_key: str, db: DB, ai_config: AIConfig):
        self.client = OpenAI(api_key=openai_api_key)
        self.db = db
        self.ai_config = ai_config

    async def _get_default_text_model_name(self) -> str:
        first_model = None
        for model in self.ai_config.TextGeneration.Models.values():
            if model.is_default:
                return model.name
            if first_model is None:
                first_model = model.name
        return first_model

    async def describe_image(self, in_memory_image_stream: io.BytesIO) -> str:
        # TODO: implement this
        # r = await openai.Image.adescribe(in_memory_image_stream)
        # return r["description"] or ""
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

    async def get_reply(self, user_input: str) -> str:
        response = self.client.chat.completions.create(
            model=self._get_default_text_model_name(),
            messages=[
                {"role": "system", "content": f"User: {user_input}"},
                {"role": "user", "content": user_input},
            ],
            temperature=self.ai_config.TextGeneration.temperature,
        )
        return response.choices[0].message.content

    async def get_streaming_reply(self, user_input: str) -> AsyncIterator[str]:
        response = self.client.chat.completions.create(
            model=self._get_default_text_model_name(),
            messages=[
                {"role": "system", "content": f"User: {user_input}"},
                {"role": "user", "content": user_input},
            ],
            stream=True,
            temperature=self.ai_config.TextGeneration.temperature,
        )
        for chunk in response:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
