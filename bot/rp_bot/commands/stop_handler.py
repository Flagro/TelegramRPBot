from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    command = "stop"
    list_priority_order = CommandPriority.FIRST

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        await self.db.chats.stop_chat(context)
        return CommandResponse(text="stop_done")
