from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseHandler, BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned


class ShowChatModesHandler(BaseHandler):
    _show_chat_modes_callback = "show_chat_modes"

    async def _get_chat_modes_keyboard(
        self, context: Context, callback_action: str
    ) -> KeyboardResponse:
        available_modes = await self.db.chat_modes.get_chat_modes(context)
        modes_dict = OrderedDict(
            {str(mode.id): str(mode.mode_name) for mode in available_modes}
        )
        return CommandResponse(
            text="choose_mode",
            keyboard=KeyboardResponse(
                modes_dict=modes_dict,
                callback=self._show_chat_modes_callback,
                button_action=callback_action,
            ),
        )


class CallbackHandler(BaseCallbackHandler, ShowChatModesHandler):
    permissions = [AllowedUser, NotBanned]
    callback_action = ShowChatModesHandler._show_chat_modes_callback

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse(
            keyboard=self._get_chat_modes_keyboard(
                context=context,
                callback_action=args[0],
            ),
        )
