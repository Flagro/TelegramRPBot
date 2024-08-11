from typing import List

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..callbacks.set_chat_language_handler import CallbackHandler
from ..callbacks.show_chat_languages_handler import ShowChatLanguagesMixin


class CommandHandler(BaseCommandHandler, ShowChatLanguagesMixin):
    permissions = CallbackHandler.permissions
    command = "language"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        return CommandResponse(
            text="choose_language",
            keyboard=self._get_chat_languages_keyboard(
                db=self.db,
                context=context,
                callback_action=CallbackHandler.callback_action,
            ),
        )
