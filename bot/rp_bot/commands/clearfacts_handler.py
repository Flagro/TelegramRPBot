from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    command = "clearfacts"
    list_priority_order = 1

    async def get_command_response(
        self, person: Person, context: Context, args
    ) -> CommandResponse:
        facts_user_handle = args[0]
        chat_id = context.chat_id
        self.db.clear_facts(chat_id, facts_user_handle)
        return CommandResponse(
            "facts_cleared", {"user_handle": facts_user_handle}, None
        )
