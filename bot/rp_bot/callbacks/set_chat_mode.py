@callback_handler
@authorized
async def _set_chat_mode(self, chat_id, args) -> CommandResponse:
    mode_id = args[0]
    self.db.set_chat_mode(chat_id, mode_id)
    return CommandResponse("mode_set", {"mode_id": mode_id}, None)

pattern = "^set_chat_mode"
