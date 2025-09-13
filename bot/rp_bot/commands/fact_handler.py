from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (AllowedUser, NotBanned)
    command = "fact"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        if not args or len(args) < 2:
            return CommandResponse(text="invalid_fact_args")
        facts_user_handle = args[0]
        if not facts_user_handle.startswith("@"):
            facts_user_handle = "@" + facts_user_handle
        facts = " ".join(args[1:])
        try:
            await self.db.user_facts.add_fact(context, facts_user_handle, facts)
            return CommandResponse(
                text="fact_added", kwargs={"user_handle": facts_user_handle}
            )
        except ValueError as e:
            self.logger.error(f"Error adding fact: {e}")
            return CommandResponse(text="inappropriate_fact")
