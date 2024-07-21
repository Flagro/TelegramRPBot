from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    command = "usage"
    list_priority_order = 3

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_usage = await self.db.users.get_user_usage(person)
        return CommandResponse("usage_text", user_usage._asdict())
