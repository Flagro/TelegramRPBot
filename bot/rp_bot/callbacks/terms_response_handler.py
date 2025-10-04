from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCallbackHandler
from ..auth import AllowedUser, NotBanned


class CallbackHandler(RPBotCallbackHandler):
    permission_classes = (AllowedUser, NotBanned)
    callback_action = "terms_response"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        # args[0] should be "terms_action", args[1] should be "accept" or "decline"
        if len(args) < 2:
            return CommandResponse(text="invalid_terms_action")

        action = args[1]  # "accept" or "decline"

        if action == "accept":
            await self.auth.accept_terms(person.user_handle)
            return CommandResponse(text="terms_accepted")
        elif action == "decline":
            await self.auth.decline_terms(person.user_handle)
            return CommandResponse(text="terms_declined")
        else:
            return CommandResponse(text="invalid_terms_action")
