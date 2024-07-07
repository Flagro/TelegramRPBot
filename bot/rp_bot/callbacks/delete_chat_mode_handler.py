from typing import List

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..commands.deletemode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "delete_chat_mode"

    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        mode_id = args[0]
        mode_name = await self.db.get_mode_name_by_id(context, mode_id)
        await self.db.delete_chat_mode(context, mode_id)
        return CommandResponse("mode_deleted", {"mode_name": mode_name})
