from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (AllowedUser, NotBanned)
    command = "usage"
    list_priority_order = CommandPriority.LAST

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_usage = await self.db.users.get_user_usage_report(person)
        return CommandResponse(
            text="usage_text", kwargs={"this_month_usage": user_usage.this_month_usage}
        )
