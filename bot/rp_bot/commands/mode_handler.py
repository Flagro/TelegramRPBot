from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(BaseCommandHandler):
    permissions = [GroupAdmin, AllowedUser, NotBanned]
    command = "mode"
    list_priority_order = 2

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        available_modes = await self.db.chat_modes.get_chat_modes(context)
        modes_dict = OrderedDict(
            {str(mode.id): str(mode.mode_name) for mode in available_modes}
        )
        return CommandResponse(
            text="choose_mode",
            kwargs={},
            keyboard=KeyboardResponse(
                modes_dict=modes_dict,
                callback="show_chat_modes",
                button_action="set_chat_mode",
            ),
        )
