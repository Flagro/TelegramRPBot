from ..rp_bot.db import DB
from .config.localizer_translations import LocalizerTranslations
from ..models.handlers_input import Person, Context, Message


class Localizer:
    def __init__(self, db: DB, translations: LocalizerTranslations) -> None:
        self.db: DB = db
        self.translations: LocalizerTranslations = translations

    async def set_language(self, context: Context, language: str) -> None:
        await self.db.set_language(context, language)

    def compose_user_input(
        self, message: str, image_description: str, voice_description: str
    ) -> str:
        return (
            f"{message}\n{image_description}\n{voice_description}"
        )
        
    async def compose_history_message(self, context: Context) -> str:
        messages = await self.db.get_messages(context)
        return "\n".join(messages)

    def get_command_response(self, text: str, kwargs: dict) -> str:
        return self.translations.get_command_response(text, kwargs)
