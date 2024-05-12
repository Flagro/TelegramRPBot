from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import ListResponse
from ..commands.mode_handler import CommandHandler


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes" # TODO: add "^" concat in TG handler
    
    async def get_callback_response(self, chat_id, args) -> ListResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        return ListResponse(available_modes, self.callback_action)
