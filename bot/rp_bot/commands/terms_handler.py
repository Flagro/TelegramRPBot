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
        # Check current user state
        has_accepted = await self.auth.has_accepted_terms(person.user_handle)
        has_declined = await self.auth.has_declined_terms(person.user_handle)

        # Always show the full terms with keyboard
        if has_accepted:
            # User has already accepted terms - show extra prompt
            return CommandResponse(
                text="terms_text",
                keyboard=await self._get_terms_keyboard(context),
            )
        elif has_declined:
            # User has declined terms - show extra prompt
            return CommandResponse(
                text="terms_text",
                keyboard=await self._get_terms_keyboard(context),
            )
        else:
            # User hasn't made a decision yet - show standard terms
            return CommandResponse(
                text="terms_text",
                keyboard=await self._get_terms_keyboard(context),
            )
