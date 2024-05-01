from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    permissions = []

    async def get_command_response(self, chat_id) -> CommandResponse:
        self.db.reset(chat_id)
        return CommandResponse("reset_done", {}, None)
