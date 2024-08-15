from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(BaseCommandHandler):
    permission_classes = [GroupAdmin, AllowedUser, NotBanned]
    command = "clearfacts"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        facts_user_handle = args[0]
        await self.db.user_facts.clear_facts(context, facts_user_handle)
        return CommandResponse(
            text="facts_cleared", kwargs={"user_handle": facts_user_handle}
        )
