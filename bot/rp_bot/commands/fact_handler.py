from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    command_name = "fact"
    list_priority_order = 1

    async def get_command_response(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        facts = " ".join(args[1:])
        try:
            self.db.add_fact(chat_id, facts_user_handle, facts)
            return CommandResponse("fact_added", {"user_handle": facts_user_handle})
        except ValueError as e:
            self.logger.error(f"Error adding fact: {e}")
            return CommandResponse("inappropriate_fact", {}, None)
