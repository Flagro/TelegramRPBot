from ..rp_bot.db import DB
from .config.localizer_translations import LocalizerTranslations


class Localizer:
    def __init__(self, db: DB, translations: LocalizerTranslations) -> None:
        self.db = db
        self.translations = translations

    def set_language(self, chat_id: str, language: str) -> None:
        self.db.set_language(chat_id, language)

    def compose_user_input(
        self, message: str, image_description: str, voice_description: str
    ) -> str:
        return (
            f"{message}\n{image_description}\n{voice_description}"
        )
        
    def compose_history_message(self, chat_id) -> str:
        messages = self.db.get_messages(chat_id, 100)
        return "\n".join(messages)

    def get_command_response(self, text: str, kwargs: dict) -> str:
        return self.translations.get_command_response(text, kwargs)
