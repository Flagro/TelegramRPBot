from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    permissions = []

    async def get_command_response(self) -> CommandResponse:
        return CommandResponse("help_text", {}, None)
