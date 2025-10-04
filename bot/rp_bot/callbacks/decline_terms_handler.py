from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCallbackHandler
from ..auth import AllowedUser, NotBanned


class CallbackHandler(RPBotCallbackHandler):
    permission_classes = (AllowedUser, NotBanned)
    callback_action = "decline_terms"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        await self.auth.decline_terms(person.user_handle)
        return CommandResponse(text="terms_declined")
