import tiktoken
import openai
import io
from collections import namedtuple


AIResponse = namedtuple("AIResponse", ["text", "image_url"])


async def generate_images(prompt, n_images=4, size="512x512"):
    r = await openai.Image.acreate(prompt=prompt, n=n_images, size=size)
    image_urls = [item.url for item in r.data]
    return image_urls


async def is_content_acceptable(text: str):
    r = await openai.Moderation.acreate(input=text)
    return not all(r.results[0].categories.values())

class AI:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
    def describe_image(self, in_memory_image_stream: io.BytesIO):
        r = openai.Image.adescribe(in_memory_image_stream)
        return r["description"] or ""
    
    def transcribe_audio(self, in_memory_audio_stream: io.BytesIO):
        r = openai.Audio.atranscribe(in_memory_audio_stream)
        return r["text"] or ""

    def get_reply(self, chat_id: str, user_handle: str, user_input: str) -> AIResponse:
        pass

