from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (BotAdmin,)
    command = "unban"
    list_priority_order = CommandPriority.ADMIN

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_handle = args[0]
        await self.db.users.unban_user(user_handle)
        return CommandResponse(
            text="user_unbanned", kwargs={"user_handle": user_handle}
        )
