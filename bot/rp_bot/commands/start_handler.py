from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(BaseCommandHandler):
    permission_classes = [GroupAdmin, AllowedUser, NotBanned]
    command = "start"
    list_priority_order = CommandPriority.FIRST

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        await self.db.chats.start_chat(context)
        return CommandResponse(text="start_done")
