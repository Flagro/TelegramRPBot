from .db import DB


class Localizer:
    def __init__(self, db: DB, translations: dict) -> None:
        self.db = db

    def set_language(self, chat_id: str, language: str) -> None:
        self.db.set_language(chat_id, language)

    def compose_user_input(
        self, message: str, image_description: str, voice_description: str
    ) -> str:
        pass

    def get_command_response(self, text: str, kwargs: dict) -> tuple[str, str]:
        pass
