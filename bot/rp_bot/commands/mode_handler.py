from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import ListResponse
from ..auth import AllowedUser


class CommandHandler(BaseCommandHandler):
    permissions = [AllowedUser]
    list_priority_order = 1

    async def get_command_response(self, chat_id) -> ListResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_names = [mode.name for mode in available_modes]
        modes_ids = [mode.id for mode in available_modes]
        return ListResponse(
            "choose_mode",
            {},
            "show_chat_modes",
            "set_chat_mode",
            modes_names,
            modes_ids,
        )
