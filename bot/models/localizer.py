from typing import Optional, List, Tuple
from .config.localizer_translations import LocalizerTranslations


class Localizer:
    def __init__(self, translations: LocalizerTranslations) -> None:
        self.translations: LocalizerTranslations = translations

    def compose_user_input(
        self, message: str, image_description: Optional[str], voice_description: Optional[str]
    ) -> str:
        # TODO: also add user name and context details
        result = [message]
        if image_description:
            result.append(image_description)
        if voice_description:
            result.append(voice_description)
        return " ".join(result)
        
    async def compose_history_message(self, history: List[Tuple[str, str]]) -> str:
        # TODO: also add the names and context details in history
        return "\n".join([f"{name}: {message}" for name, message in history])

    def get_command_response(self, text: str, kwargs: dict) -> str:
        return self.translations.get_command_response(text, kwargs)
