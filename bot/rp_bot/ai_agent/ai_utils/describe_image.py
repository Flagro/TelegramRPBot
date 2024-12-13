import io
import base64
from typing import Literal, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from .base_utility import BaseUtility


class ImageInformation(BaseModel):
    # TODO: move this to prompt manager
    image_description: str = Field(description="a short description of the image")
    image_type: Literal["screenshot", "picture", "selfie", "anime"] = Field(
        description="type of the image"
    )
    main_objects: List[str] = Field(
        description="list of the main objects on the picture"
    )

    def __str__(self):
        main_objects_prompt = ", ".join(self.main_objects)
        return (
            f'Image description: "{self.image_description}", '
            f'Image type: "{self.image_type}", '
            f'Main objects: "{main_objects_prompt}"'
        )


class DescribeImageUtililty(BaseUtility):
    def run(self, in_memory_image_stream: io.BytesIO) -> ImageInformation:
        # Encode in base64:
        image_base64 = base64.b64encode(in_memory_image_stream.getvalue()).decode()
        parser = JsonOutputParser(pydantic_object=ImageInformation)

        # TODO: implement image chain runnable
        # TODO: pass the image model here

        return ImageInformation(
            image_description="an image", image_type="picture", main_objects=["image"]
        )

    async def arun(self, in_memory_image_stream: io.BytesIO) -> ImageInformation:
        # TODO: make it non-blocking
        return self.run(in_memory_image_stream)
