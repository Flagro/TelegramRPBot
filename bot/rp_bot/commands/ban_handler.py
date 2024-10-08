from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCommandHandler
from ..auth import BotAdmin


class CommandHandler(RPBotCommandHandler):
    permission_classes = (BotAdmin,)
    command = "ban"
    list_priority_order = CommandPriority.ADMIN

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        if context.replied_to_user_handle is None:
            user_handle = args[0]
            time_seconds = int(args[1])
        else:
            user_handle = context.replied_to_user_handle
            time_seconds = int(args[1])
        await self.db.users.ban_user(user_handle, time_seconds)
        return CommandResponse(
            text="user_banned",
            kwargs={"user_handle": user_handle, "ban_duration": time_seconds},
        )
