from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import KeyboardResponse, CommandResponse
from ..commands.mode_handler import CommandHandler
from ...models.handlers_input import Person, Context


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes"

    async def get_callback_response(
        self, person: Person, context: Context, args
    ) -> CommandResponse:
        chat_id = context.chat_id
        old_action = args[0]
        available_modes = self.db.get_chat_modes(chat_id)
        modes_dict = {mode.id: mode.name for mode in available_modes}

        return CommandResponse(
            "choose_mode_to_delete",
            {},
            KeyboardResponse(
                modes_dict,
                "show_chat_modes",
                old_action,
            )
        )
