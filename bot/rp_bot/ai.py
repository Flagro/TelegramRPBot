import tiktoken
import openai
import io
from typing import Any
from collections import namedtuple

from .db import DB


AIResponse = namedtuple("AIResponse", ["text", "image_url"])


def count_tokens(text: str):
    return tiktoken.count(text)


async def is_content_acceptable(text: str):
    r = await openai.Moderation.acreate(input=text)
    return not all(r.results[0].categories.values())

class AI:
    def __init__(self, openai_api_key: str, db: DB, ai_config: Any):
        self.openai_api_key = openai_api_key
        self.db = db
        self.ai_config = ai_config
        
    async def describe_image(self, in_memory_image_stream: io.BytesIO):
        r = await openai.Image.adescribe(in_memory_image_stream)
        return r["description"] or ""
    
    async def transcribe_audio(self, in_memory_audio_stream: io.BytesIO):
        r = await openai.Audio.atranscribe(in_memory_audio_stream)
        return r["text"] or ""
    
    async def generate_image(self, prompt: str):
        r = await openai.Image.acreate(prompt=prompt, n=1, size="512x512")
        image_url = r.data[0].url
        return image_url

    async def get_reply(self, user_input: str) -> AIResponse:
        r = await openai.Chat.agenerate(
            model=self.ai_config.model,
            messages=[
                {"role": "system", "content": f"User: {user_input}"},
                {"role": "user", "content": user_input},
            ],
        )
        return AIResponse(text=r.choices[0].message.content, image_url=None)
