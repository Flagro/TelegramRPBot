from typing import List

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CallbackHandler(BaseCallbackHandler):
    permissions = [GroupAdmin, AllowedUser, NotBanned]
    callback_action = "set_chat_language"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        language = args[0]
        await self.db.chats.set_language(context, language)
        return CommandResponse(text="language_set", kwargs={"language": language})
