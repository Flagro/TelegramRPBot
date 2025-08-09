from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCommandHandler
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(RPBotCommandHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    command = "clearfacts"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        facts_user_handle = args[0]
        await self.db.user_facts.clear_facts(context, facts_user_handle)
        return CommandResponse(
            text="facts_cleared", kwargs={"user_handle": facts_user_handle}
        )
