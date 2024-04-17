@command_handler
@authorized
async def _reset(self, chat_id) -> CommandResponse:
    self.db.reset(chat_id)
    return CommandResponse("reset_done", {}, None)
