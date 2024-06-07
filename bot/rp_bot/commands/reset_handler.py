from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    command = "reset"
    list_priority_order = 1

    async def get_command_response(
        self, person: Person, context: Context, args
    ) -> CommandResponse:
        chat_id = context.chat_id
        self.db.reset(chat_id)
        return CommandResponse("reset_done", {})
