from typing import List

from ...models.base_handlers import CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCommandHandler
from ..auth import AllowedUser, NotBanned


class CommandHandler(RPBotCommandHandler):
    permission_classes = (AllowedUser, NotBanned)
    command = "terms"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        # TODO: use different prompts depending on these states:
        # has_accepted = await self.auth.has_accepted_terms(person.user_handle)
        # has_declined = await self.auth.has_declined_terms(person.user_handle)

        return CommandResponse(
            text="terms_text",
            keyboard=await self._get_terms_keyboard(context),
        )
