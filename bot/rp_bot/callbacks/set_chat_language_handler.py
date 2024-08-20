from typing import List

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..rp_bot_handlers import RPBotCallbackHandler
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CallbackHandler(RPBotCallbackHandler):
    permission_classes = (GroupAdmin, AllowedUser, NotBanned)
    callback_action = "set_chat_language"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        language = args[0]
        await self.db.chats.set_language(context, language)
        return CommandResponse(text="language_set", kwargs={"language": language})
