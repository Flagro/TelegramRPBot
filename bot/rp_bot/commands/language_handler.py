from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    command = "language"
    list_priority_order = 3

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        if len(args) == 0:
            return CommandResponse("specify_language", {})
        language = args[0]
        try:
            await self.db.chats.set_language(context, language)
            return CommandResponse("language_set", {"language": language})
        except ValueError as e:
            self.logger.error(f"Error setting language: {e}")
            return CommandResponse("language_set_error", {"language": language})
