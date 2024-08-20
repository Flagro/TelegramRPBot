from typing import List
from collections import OrderedDict

from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCallbackHandler
from ..db import DB
from ..auth import AllowedUser, NotBanned


class ShowChatLanguagesMixin:
    _show_chat_languages_callback = "show_chat_languages"

    async def _get_chat_languages_keyboard(
        self, db: DB, context: Context, callback_action: str
    ) -> KeyboardResponse:
        available_modes = await db.chat_modes.get_chat_modes(context)
        modes_dict = OrderedDict(
            {str(mode.id): str(mode.mode_name) for mode in available_modes}
        )
        return KeyboardResponse(
            modes_dict=modes_dict,
            callback=self._show_chat_languages_callback,
            button_action=callback_action,
        )


class CallbackHandler(ShowChatLanguagesMixin, RPBotCallbackHandler):
    permission_classes = (AllowedUser, NotBanned)
    callback_action = ShowChatLanguagesMixin._show_chat_languages_callback

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse(
            keyboard=self._get_chat_languages_keyboard(
                db=self.db,
                context=context,
                callback_action=args[0],
            ),
        )
