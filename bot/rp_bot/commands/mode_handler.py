from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import KeyboardResponse
from ...models.handlers_input import Person, Context
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    command = "mode"
    list_priority_order = 1

    async def get_command_response(
        self, person: Person, context: Context
    ) -> KeyboardResponse:
        chat_id = context.chat_id
        available_modes = self.db.get_chat_modes(chat_id)
        modes_dict = {mode.id: mode.name for mode in available_modes}
        return KeyboardResponse(
            "choose_mode",
            {},
            "show_chat_modes",
            "set_chat_mode",
            modes_dict
        )
