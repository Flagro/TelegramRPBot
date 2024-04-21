@command_handler
@authorized
async def _clearfacts(self, chat_id, args) -> CommandResponse:
    facts_user_handle = args[0]
    self.db.clear_facts(chat_id, facts_user_handle)
    return CommandResponse(
        "facts_cleared", {"user_handle": facts_user_handle}, None
    )
