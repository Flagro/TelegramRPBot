from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, NotBanned
from ..rp_bot_handlers import RPBotCommandHandler


class CommandHandler(RPBotCommandHandler):
    permission_classes = (AllowedUser, NotBanned)
    command = "facts"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        facts_user_handle = args[0]
        if not facts_user_handle:
            facts_user_handle = person.user_handle
        facts = await self.db.user_facts.get_facts_for_user_handle(
            context, facts_user_handle
        )
        facts_prompt = "\n- ".join(facts)
        return CommandResponse(
            text="user_facts",
            kwargs={"user_handle": facts_user_handle, "facts": facts_prompt},
        )
