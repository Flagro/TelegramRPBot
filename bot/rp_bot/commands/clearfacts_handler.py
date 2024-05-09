from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    list_priority_order = 1

    async def get_command_response(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        self.db.clear_facts(chat_id, facts_user_handle)
        return CommandResponse(
            "facts_cleared", {"user_handle": facts_user_handle}, None
        )
