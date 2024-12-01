import io
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from .base_utility import BaseUtility


class AudioInformation(BaseModel):
    # TODO: move this to prompt manager
    audio_description: str = Field(description="a short description of the audio")

    def __str__(self):
        return self.audio_description


async def describe_audio(in_memory_image_stream: io.BytesIO) -> AudioInformation:
    # Encode in base64:
    parser = JsonOutputParser(pydantic_object=AudioInformation)

    # TODO: implement moderation

    return AudioInformation(audio_description="an audio")


class DescribeAudioUtililty(BaseUtility):
    def run(self, in_memory_image_stream: io.BytesIO) -> AudioInformation:
        return describe_audio(in_memory_image_stream)

    async def arun(self, in_memory_image_stream: io.BytesIO) -> AudioInformation:
        return await describe_audio(in_memory_image_stream)
