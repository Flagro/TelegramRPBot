@command_handler
@authorized
async def _introduce(self, chat_id, user_handle, args) -> CommandResponse:
    introduction = " ".join(args)
    try:
        self.db.add_introduction(chat_id, user_handle, introduction)
        return CommandResponse("introduction_added", {"user_handle": user_handle})
    except ValueError as e:
        self.logger.error(f"Error adding introduction: {e}")
        return CommandResponse("inappropriate_introduction", {}, None)
