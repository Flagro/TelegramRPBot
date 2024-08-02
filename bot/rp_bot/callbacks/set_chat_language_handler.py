from typing import List

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "set_chat_language"

    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        language = args[0]
        await self.db.chats.set_language(context, language)
        return CommandResponse("language_set", {"language": language})
