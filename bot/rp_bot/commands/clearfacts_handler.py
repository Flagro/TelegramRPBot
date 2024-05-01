from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    permissions = []

    async def get_command_response(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        self.db.clear_facts(chat_id, facts_user_handle)
        return CommandResponse(
            "facts_cleared", {"user_handle": facts_user_handle}, None
        )
