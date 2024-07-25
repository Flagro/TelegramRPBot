from typing import List

from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin, NotBanned


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin, NotBanned]
    command = "conversationtracker"
    list_priority_order = 3

    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        new_value = await self.db.chats.switch_conversation_tracker(context)
        return CommandResponse(
            (
                "conversation_tracker_turned_on"
                if new_value
                else "conversation_tracker_turned_off"
            ),
            {},
        )
