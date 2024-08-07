from typing import List
from collections import OrderedDict

from ...models.base_handlers import BaseCommandHandler, CommandPriority
from ...models.handlers_response import CommandResponse, KeyboardResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CommandHandler(BaseCommandHandler):
    permissions = [GroupAdmin, AllowedUser, NotBanned]
    command = "language"
    list_priority_order = CommandPriority.DEFAULT

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        available_languages = await self.localizer.get_supported_languages()
        languages_dict = OrderedDict(
            {str(language): str(language) for language in available_languages}
        )
        return CommandResponse(
            text="choose_language",
            keyboard=KeyboardResponse(
                modes_dict=languages_dict,
                callback="show_chat_languages",
                button_action="set_chat_language",
            ),
        )
