from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse


class CallbackHandler(BaseCallbackHandler):
    permissions = []
    pattern = "^set_chat_mode"
    
    async def get_callback_response(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.set_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_set", {"mode_id": mode_id}, None)
