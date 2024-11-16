import io

from openai import OpenAI


class Moderation:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

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
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=image_description,
        )
        flagged = response["results"][0]["flagged"]
        if flagged:
            return False
        return True

    def moderate_audio_description(self, audio_description: str) -> bool:
        """
        Moderates the audio and returns True if the audio is safe
        """
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=audio_description,
        )
        flagged = response["results"][0]["flagged"]
        if flagged:
            return False
        return True

    def moderate_text(self, text: str) -> bool:
        """
        Moderates the text and returns True if the text is safe
        """
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )
        flagged = response["results"][0]["flagged"]
        if flagged:
            return False
        return True
