@callback_handler
@authorized
async def _delete_chat_mode(self, chat_id, args) -> CommandResponse:
    mode_id = args[0]
    self.db.delete_chat_mode(chat_id, mode_id)
    return CommandResponse("mode_deleted", {"mode_id": mode_id}, None)
