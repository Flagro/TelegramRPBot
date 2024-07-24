from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    command = "ban"
    list_priority_order = 2

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_handle = args[0]
        time_seconds = int(args[1])
        await self.db.users.ban_user(context, user_handle, time_seconds)
        return CommandResponse("user_banned", {"user_handle": user_handle})
