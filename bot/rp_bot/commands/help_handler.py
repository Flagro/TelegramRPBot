from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AnyUser


class CommandHandler(BaseCommandHandler):
    permissions = [AnyUser]
    command = "help"
    list_priority_order = 4

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse("help_text", {})
