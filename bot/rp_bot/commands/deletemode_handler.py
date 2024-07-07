from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    command = "deletemode"
    list_priority_order = 1

    async def get_command_response(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> CommandResponse:
        available_modes = await self.db.get_chat_modes(context)
        modes_dict = OrderedDict({mode.id: mode.name for mode in available_modes})
        return CommandResponse(
            "choose_mode_to_delete",
            {},
            KeyboardResponse(
                modes_dict,
                "show_chat_modes",
                "delete_chat_mode",
            )
        )
