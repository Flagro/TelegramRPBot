from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes"

    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        old_action = args[0]
        available_modes = self.db.get_chat_modes(context)
        modes_dict = OrderedDict({mode.id: mode.name for mode in available_modes})

        return CommandResponse(
            "choose_mode_to_delete",
            {},
            KeyboardResponse(
                modes_dict,
                "show_chat_modes",
                old_action,
            )
        )
