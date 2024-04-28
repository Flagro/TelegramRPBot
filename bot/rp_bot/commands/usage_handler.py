from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    async def handle(self, user_handle) -> CommandResponse:
        user_usage = self.db.get_user_usage(user_handle)
        return CommandResponse("usage_text", user_usage._asdict(), None)
