from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    command = "reset"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        await self.db.dialogs.reset(context)
        return CommandResponse(text="reset_done")
