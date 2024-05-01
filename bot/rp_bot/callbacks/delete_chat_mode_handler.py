from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse


class CallbackHandler(BaseCallbackHandler):
    permissions = []
    pattern = "^delete_chat_mode"
    
    async def get_callback_response(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.delete_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_deleted", {"mode_id": mode_id}, None)
