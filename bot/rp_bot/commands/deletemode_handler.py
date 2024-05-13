from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import ListResponse
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    list_priority_order = 1

    async def get_command_response(self, chat_id) -> ListResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        return ListResponse(
            "choose_mode_to_delete",
            {},
            "show_chat_modes",
            "delete_chat_mode",
            available_modes,
        )
