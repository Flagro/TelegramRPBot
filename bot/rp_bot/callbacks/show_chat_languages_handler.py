from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_languages"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        old_action = args[0]
        available_languages = await self.localizer.get_supported_languages()
        languages_dict = OrderedDict(
            {language: language for language in available_languages}
        )
        return CommandResponse(
            text="choose_language",
            keyboard=KeyboardResponse(
                modes_dict=languages_dict,
                callback="show_chat_languages",
                button_action=old_action,
            ),
        )
