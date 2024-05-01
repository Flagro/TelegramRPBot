from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse


class CommandHandler(BaseCommandHandler):
    permissions = []

    async def get_command_response(self, chat_id, args) -> CommandResponse:
        language = args[0]
        try:
            self.localizer.set_language(chat_id, language)
            return CommandResponse("language_set", {"language": language})
        except ValueError as e:
            self.logger.error(f"Error setting language: {e}")
            return CommandResponse("language_set_error", {"language": language}, None)
