import io
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from ..models_toolkit import ModelsToolkit
from ....models.handlers_input import Person, Context, Message


class AudioInformation(BaseModel):
    # TODO: move this to prompt manager
    audio_description: str = Field(description="a short description of the audio")


async def describe_audio(in_memory_image_stream: io.BytesIO) -> AudioInformation:
    # Encode in base64:
    parser = JsonOutputParser(pydantic_object=AudioInformation)

    # TODO: implement moderation

    return AudioInformation(
        audio_description="an audio"
    )


class DescribeAudioUtililty:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        models_toolkit: ModelsToolkit,
    ):
        self.person = person
        self.context = context
        self.message = message
        self.models_toolkit = models_toolkit

    def run(self, in_memory_image_stream: io.BytesIO) -> AudioInformation:
        return describe_audio(in_memory_image_stream)
