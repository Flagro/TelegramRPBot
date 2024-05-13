from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import ListResponse
from ..commands.mode_handler import CommandHandler


class CallbackHandler(BaseCallbackHandler):
    permissions = CommandHandler.permissions
    callback_action = "show_chat_modes"  # TODO: add "^" concat in TG handler

    async def get_callback_response(self, chat_id, args) -> ListResponse:
        old_action = args[0]
        available_modes = self.db.get_chat_modes(chat_id)
        return ListResponse(
            "choose_mode_to_delete",
            {},
            "show_chat_modes",
            old_action,
            available_modes,
        )
