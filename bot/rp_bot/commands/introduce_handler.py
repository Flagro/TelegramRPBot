from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser, NotBanned]
    command = "introduce"
    list_priority_order = 2

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_handle = person.user_handle
        introduction = " ".join(args)
        try:
            await self.db.user_introductions.add_introduction(
                context, user_handle, introduction
            )
            return CommandResponse(
                text="introduction_added", kwargs={"user_handle": user_handle}
            )
        except ValueError as e:
            self.logger.error(f"Error adding introduction: {e}")
            return CommandResponse(text="inappropriate_introduction")
