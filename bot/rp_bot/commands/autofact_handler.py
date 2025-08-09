from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCommandHandler
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(RPBotCommandHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    command = "autofact"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        new_value = await self.db.chats.switch_auto_fact(context)
        return CommandResponse(
            text=(
                "autofact_turned_on"
                if new_value
                else "autofact_turned_off"
            ),
        )
