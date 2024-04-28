from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ..keyboards import get_chat_modes_keyboard


class CommandHandler(BaseCommandHandler):
    async def handle(self, chat_id) -> CommandResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", "set_chat_mode"
        )
        return CommandResponse("choose_mode", {}, modes_keyboard)
