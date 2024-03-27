class Localizer:
    def __init__(self):
        pass

    def set_language(self, chat_id: str, language: str) -> None:
        pass

    def compose_user_input(
        self, message: str, image_description: str, voice_description: str
    ) -> str:
        pass

    def get_command_response(self, text: str, kwargs: dict) -> tuple[str, str]:
        pass
