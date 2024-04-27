from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..keyboards import get_chat_modes_keyboard


class CallbackHandler(BaseCallbackHandler):
    pattern = "^show_chat_modes"
    
    async def handle(self, chat_id, args) -> CommandResponse:
        button_action = args[0]
        page_index = int(args[1])
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", button_action, page_index
        )
        return CommandResponse("", {}, modes_keyboard)
