@command_handler
async def _help(self) -> CommandResponse:
    return CommandResponse("help_text", {}, None)
