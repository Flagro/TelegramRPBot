from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..commands.deletemode_handler import CommandHandler
from ...models.handlers_input import Person, Context


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "delete_chat_mode"

    async def get_callback_response(
        self, person: Person, context: Context, args
    ) -> CommandResponse:
        chat_id = context.chat_id
        mode_id = args[0]
        self.db.delete_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_deleted", {"mode_id": mode_id})
