@command_handler
@authorized
async def _usage(self, user_handle) -> CommandResponse:
    user_usage = self.db.get_user_usage(user_handle)
    return CommandResponse("usage_text", user_usage._asdict(), None)
