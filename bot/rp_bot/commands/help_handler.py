from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ..auth import AnyUser


class CommandHandler(BaseCommandHandler):
    permissions = [AnyUser]
    command = "help"
    list_priority_order = 3

    async def get_command_response(self) -> CommandResponse:
        return CommandResponse("help_text", {}, None)
