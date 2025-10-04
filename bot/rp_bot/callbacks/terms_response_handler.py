from typing import List
from collections import OrderedDict

from ...models.handlers_response import KeyboardResponse, CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCallbackHandler
from ..auth import AllowedUser, NotBanned


class TermsHandlerMixin:
    _terms_callback = "terms_response"

    def _get_terms_keyboard(self) -> KeyboardResponse:
        """Create keyboard for terms acceptance/decline"""
        terms_dict = OrderedDict({
            "accept": "✅ Accept Terms",
            "decline": "❌ Decline Terms",
        })
        return KeyboardResponse(
            modes_dict=terms_dict,
            callback=self._terms_callback,
            button_action="terms_action",
        )


class CallbackHandler(TermsHandlerMixin, RPBotCallbackHandler):
    permission_classes = (AllowedUser, NotBanned)
    callback_action = TermsHandlerMixin._terms_callback

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
