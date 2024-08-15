from typing import List

from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import GroupAdmin, AllowedUser, NotBanned


class CallbackHandler(BaseCallbackHandler):
    permission_classes = [GroupAdmin, AllowedUser, NotBanned]
    callback_action = "set_chat_mode"

    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        mode_id = args[0]
        mode_name = await self.db.chat_modes.get_mode_name_by_id(context, mode_id)
        await self.db.chat_modes.set_chat_mode(context, mode_id)
        return CommandResponse(text="mode_set", kwargs={"mode_name": mode_name})
