from types import SimpleNamespace

import pytest

from bot.models.config.localizer_translations import (
    LocalizerTranslation,
    LocalizerTranslations,
)
from bot.models.handlers_input import Context
from bot.rp_bot.localizer import Localizer


class FakeChats:
    def __init__(self, language: str):
        self.language = language

    async def get_language(self, context: Context) -> str:
        return self.language


def build_localizer(language: str = "en") -> Localizer:
    translations = LocalizerTranslations(
        translations={
            "greeting": LocalizerTranslation(
                language_translation={
                    "en": "Hello, {name}",
                    "es": "Hola, {name}",
                }
            ),
            "english_only": LocalizerTranslation(
                language_translation={"en": "Only English"}
            ),
        }
    )
    db = SimpleNamespace(chats=FakeChats(language))
    return Localizer(db=db, translations=translations, default_language="en")


@pytest.mark.asyncio
async def test_localizer_uses_context_language():
    localizer = build_localizer(language="es")

    response = await localizer.get_command_response(
        "greeting",
        kwargs={"name": "Ada"},
        context=Context(chat_id=1),
    )

    assert response == "Hola, Ada"


@pytest.mark.asyncio
async def test_localizer_falls_back_to_default_language():
    localizer = build_localizer(language="fr")

    response = await localizer.get_command_response(
        "greeting",
        kwargs={"name": "Ada"},
        context=Context(chat_id=1),
    )

    assert response == "Hello, Ada"


@pytest.mark.asyncio
async def test_localizer_returns_none_for_unknown_key():
    localizer = build_localizer()

    assert await localizer.get_command_response("missing") is None
