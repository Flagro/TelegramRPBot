from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    list_priority_order = 1

    async def get_command_response(self, chat_id) -> CommandResponse:
        self.db.reset(chat_id)
        return CommandResponse("reset_done", {}, None)
