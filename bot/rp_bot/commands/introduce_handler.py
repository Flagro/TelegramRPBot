from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    needs_terms_accepted = True
    permission_classes = (AllowedUser, NotBanned)
    command = "introduce"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        user_handle = person.user_handle
        introduction = " ".join(args)
        try:
            await self.db.user_introductions.add_introduction(
                context, user_handle, introduction
            )
            return CommandResponse(
                text="introduction_added", kwargs={"user_handle": user_handle}
            )
        except ValueError as e:
            self.logger.error(f"Error adding introduction: {e}")
            return CommandResponse(text="inappropriate_introduction")
