from typing import Optional, List, Tuple
from datetime import datetime
from .config.localizer_translations import LocalizerTranslations


def get_current_date_prompt() -> str:
    date_prompt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Today's date and time is: {date_prompt}. "


class Localizer:
    def __init__(
        self, translations: LocalizerTranslations, default_language: str
    ) -> None:
        self.translations: LocalizerTranslations = translations
        self.default_language: str = default_language

    async def compose_user_input(
        self,
        message: str,
        image_description: Optional[str],
        voice_description: Optional[str],
    ) -> str:
        # TODO: also add user name and context details
        result = [message]
        if image_description:
            result.append(image_description)
        if voice_description:
            result.append(voice_description)
        return " ".join(result)

    async def compose_bot_output(self, response_message: str) -> str:
        return response_message

    async def compose_prompt(
        self, user_input: str, history: List[Tuple[str, bool, str]]
    ) -> str:
        # TODO: also add the names and context details in history
        current_date_prompt = get_current_date_prompt()
        return (
            "The conversation so far:\n"
            + "\n".join([f"{name}: {message}" for name, _, message in history])
            + f"\n\n{current_date_prompt}"
            + f"\n\nAnd the user just asked: {user_input}"
        )

    async def get_command_response(
        self,
        text: str,
        kwargs: Optional[dict] = None,
        language: Optional[str] = "english",
    ) -> Optional[str]:
        if text not in self.translations.translations:
            return None
        localizer_translation = self.translations.translations[text]
        if language not in localizer_translation.language_translation:
            language = self.default_language
        if language not in localizer_translation.language_translation:
            return None
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
