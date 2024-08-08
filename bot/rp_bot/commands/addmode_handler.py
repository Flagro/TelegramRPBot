from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, GroupAdmin, NotBanned


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser, GroupAdmin, NotBanned]
    command = "addmode"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        mode_description = " ".join(args)
        # Get the first sentence or paragraph of the mode description:
        # TODO: implement NER here
        mode_name = mode_description.split("\n")[0].split(".")[0]
        try:
            await self.db.chat_modes.add_chat_mode(context, mode_name, mode_description)
            return CommandResponse(text="mode_added", kwargs={"mode_name": mode_name})
        except ValueError as e:
            self.logger.error(f"Error adding mode: {e}")
            return CommandResponse(text="inappropriate_mode")
