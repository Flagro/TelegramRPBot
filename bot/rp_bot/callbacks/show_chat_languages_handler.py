from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned


class CallbackHandler(BaseCallbackHandler):
    permissions = [AllowedUser, NotBanned]
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
                callback=self.callback_action,
                button_action=old_action,
            ),
        )
