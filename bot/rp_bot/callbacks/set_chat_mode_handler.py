from typing import List

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "set_chat_mode"

    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        chat_id = context.chat_id
        mode_id = args[0]
        self.db.set_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_set", {"mode_id": mode_id})
