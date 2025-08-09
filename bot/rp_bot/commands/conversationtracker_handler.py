from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCommandHandler
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(RPBotCommandHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    command = "conversationtracker"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        new_value = await self.db.chats.switch_conversation_tracker(context)
        return CommandResponse(
            text=(
                "conversation_tracker_turned_on"
                if new_value
                else "conversation_tracker_turned_off"
            ),
        )
