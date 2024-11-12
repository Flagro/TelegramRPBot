import io

from openai import OpenAI


class Moderation:
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


    def moderate_text(self, text: str) -> bool:
        """
        Moderates the text and returns True if the text is safe
        """
        # TODO: moderation needs a class in order to use the right credentials
        client = OpenAI()
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )
        flagged = response['results'][0]['flagged']
        if flagged:
            return False
        return True
