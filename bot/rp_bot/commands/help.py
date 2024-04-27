from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    async def handle(self) -> CommandResponse:
        return CommandResponse("help_text", {}, None)
