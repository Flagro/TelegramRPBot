from typing import Optional, List

from .db import DB
from ..models.handlers_input import Context
from ..models.config.localizer_translations import LocalizerTranslations


class Localizer:
    def __init__(
        self, db: DB, translations: LocalizerTranslations, default_language: str
    ) -> None:
        self.db = db
        self.translations: LocalizerTranslations = translations
        self.default_language: str = default_language

    async def get_command_response(
        self,
        text: str,
        kwargs: Optional[dict] = None,
        context: Optional[Context] = None,
    ) -> Optional[str]:
        if context is None:
            language = self.default_language
        else:
            language = await self.db.chats.get_language(context)
        if text not in self.translations.translations:
            return None
        localizer_translation = self.translations.translations[text]
        if language not in localizer_translation.language_translation:
            language = self.default_language
        if language not in localizer_translation.language_translation:
            return None
        if kwargs is None:
            kwargs = {}
        response_text = localizer_translation.language_translation[language].format(
            **kwargs
        )
        return response_text

    async def get_supported_languages(self) -> List[str]:
        supported_languages = set()
        for _, localizer_translation in self.translations.translations.items():
            supported_languages.update(
                localizer_translation.language_translation.keys()
            )
        return list(supported_languages)
