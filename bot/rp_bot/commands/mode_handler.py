from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..callbacks.set_chat_mode_handler import CallbackHandler
from ..callbacks.show_chat_modes_handler import ShowChatModesMixin


class CommandHandler(ShowChatModesMixin, BaseCommandHandler):
    permission_classes = CallbackHandler.permission_classes
    command = "mode"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse(
            text="choose_mode",
            keyboard=self._get_chat_modes_keyboard(
                db=self.db,
                context=context,
                callback_action=CallbackHandler.callback_action,
            ),
        )
