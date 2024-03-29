import tiktoken
import openai
import io
from collections import namedtuple


AIResponse = namedtuple("AIResponse", ["text", "image_url"])


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
    
    def generate_image(self, prompt: str):
        r = openai.Image.acreate(prompt=prompt, n=1, size="512x512")
        image_url = r.data[0].url
        return image_url

    def get_reply(self, chat_id: str, user_handle: str, user_input: str) -> AIResponse:
        pass
