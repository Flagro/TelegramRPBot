import io
import base64
from typing import Literal, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from ..models_toolkit import ModelsToolkit
from ....models.handlers_input import Person, Context, Message


class ImageInformation(BaseModel):
    # TODO: move this to prompt manager
    image_description: str = Field(description="a short description of the image")
    image_type: Literal["screenshot", "picture", "selfie", "anime"] = Field(
        description="type of the image"
    )
    main_objects: List[str] = Field(
        description="list of the main objects on the picture"
    )


async def describe_image(in_memory_image_stream: io.BytesIO) -> ImageInformation:
    # Encode in base64:
    image_base64 = base64.b64encode(in_memory_image_stream.getvalue()).decode()
    parser = JsonOutputParser(pydantic_object=ImageInformation)

    # TODO: implement moderation
    # TODO: implement image chain runnable
    # TODO: pass the image model here

    return ImageInformation(
        image_description="an image", image_type="picture", main_objects=["image"]
    )


class DescribeImageUtililty:
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

    def run(self, in_memory_image_stream: io.BytesIO) -> ImageInformation:
        return describe_image(in_memory_image_stream)
