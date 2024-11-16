import io
from typing import Optional

from openai import OpenAI


class Moderation:
    def __init__(self, model: OpenAI):
        self.client = model

    def moderate_image(self, in_memory_image_stream: io.BytesIO) -> bool:
        """
        Moderates the image and returns True if the image is safe
        """
        # TODO: implement this
        return True

    def moderate_audio(self, in_memory_audio_stream: io.BytesIO) -> bool:
        """
        Moderates the audio and returns True if the audio is safe
        """
        # TODO: implement this
        return True

    def moderate_image_description(self, image_description: str) -> bool:
        """
        Moderates the image and returns True if the image is safe
        """
        return self.moderate_text(image_description, input_description="image")

    def moderate_audio_description(self, audio_description: str) -> bool:
        """
        Moderates the audio and returns True if the audio is safe
        """
        return self.moderate_text(audio_description, input_description="audio")

    def moderate_text(self, text: str, input_description: Optional[str] = None) -> bool:
        """
        Moderates the text and returns True if the text is safe
        """
        input_formatted = f"{input_description}: {text}" if input_description else text
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=input_formatted,
        )
        flagged = response["results"][0]["flagged"]
        if flagged:
            return False
        return True
