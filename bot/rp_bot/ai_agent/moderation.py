import io

from openai import OpenAI


def moderate_image(in_memory_image_stream: io.BytesIO) -> bool:
    """
    Moderates the image and returns True if the image is safe
    """
    # TODO: implement this
    return True


def moderate_audio(in_memory_audio_stream: io.BytesIO) -> bool:
    """
    Moderates the audio and returns True if the audio is safe
    """
    # TODO: implement this
    return True


def moderate_text(text: str) -> bool:
    """
    Moderates the text and returns True if the text is safe
    """
    client = OpenAI()
    response = client.moderations.create(
        model="omni-moderation-latest",
        input="...text to classify goes here...",
    )
    flagged = response['results'][0]['flagged']
    if flagged:
        return False
    return True
