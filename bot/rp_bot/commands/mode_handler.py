from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    command = "mode"
    list_priority_order = 2

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        available_modes = await self.db.get_chat_modes(context)
        modes_dict = OrderedDict({mode.id: mode.mode_name for mode in available_modes})
        return CommandResponse(
            "choose_mode",
            {},
            KeyboardResponse(
                modes_dict,
                "show_chat_modes",
                "set_chat_mode",
            ),
        )
