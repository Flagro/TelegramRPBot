@command_handler
@authorized
async def _language(self, chat_id, args) -> CommandResponse:
    language = args[0]
    try:
        self.localizer.set_language(chat_id, language)
        return CommandResponse("language_set", {"language": language})
    except ValueError as e:
        self.logger.error(f"Error setting language: {e}")
        return CommandResponse("language_set_error", {"language": language}, None)
