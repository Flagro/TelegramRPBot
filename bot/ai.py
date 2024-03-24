import tiktoken
import openai
import openai


async def transcribe_audio(audio_file) -> str:
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"] or ""


async def generate_images(prompt, n_images=4, size="512x512"):
    r = await openai.Image.acreate(prompt=prompt, n=n_images, size=size)
    image_urls = [item.url for item in r.data]
    return image_urls


async def is_content_acceptable(prompt):
    r = await openai.Moderation.acreate(input=prompt)
    return not all(r.results[0].categories.values())

class AI:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
