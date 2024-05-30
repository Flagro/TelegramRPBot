from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context, Message


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes"

    async def get_callback_response(
        self, person: Person, context: Context, args
    ) -> KeyboardResponse:
        chat_id = context.chat_id
        old_action = args[0]
        available_modes = self.db.get_chat_modes(chat_id)
        modes_names = [mode.name for mode in available_modes]
        modes_ids = [mode.id for mode in available_modes]

        return KeyboardResponse(
            "choose_mode_to_delete",
            {},
            "show_chat_modes",
            old_action,
            modes_names,
            modes_ids,
        )
