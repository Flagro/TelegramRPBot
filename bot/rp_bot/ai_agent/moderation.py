import io

from ...models.handlers_input import Message


class ModerationError(Exception):
    pass


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
    # TODO: implement this
    return True


def moderate_user_message(message: Message) -> bool:
    """
    Moderates the user message and returns True if the message is safe
    """
    return all(
        [
            moderate_text(message.message_text),
            moderate_image(message.in_file_image) if message.in_file_image else True,
            moderate_audio(message.in_file_audio) if message.in_file_audio else True,
        ]
    )
