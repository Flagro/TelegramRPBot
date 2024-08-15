from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message


class CommandHandler(BaseCommandHandler):
    permission_classes = []
    command = "help"
    list_priority_order = CommandPriority.LAST

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse(text="help_text")
