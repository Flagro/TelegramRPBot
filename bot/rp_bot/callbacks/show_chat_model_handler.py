from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import ListResponse
from ..commands.mode_handler import CommandHandler


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes"  # TODO: add "^" concat in TG handler

    async def get_callback_response(self, chat_id, args) -> ListResponse:
        old_action = args[0]
        available_modes = self.db.get_chat_modes(chat_id)
        modes_names = [mode.name for mode in available_modes]
        modes_ids = [mode.id for mode in available_modes]
        
        return ListResponse(
            "choose_mode_to_delete",
            {},
            "show_chat_modes",
            old_action,
            modes_names,
            modes_ids,
        )
