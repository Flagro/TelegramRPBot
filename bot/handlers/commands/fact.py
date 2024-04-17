@command_handler
@authorized
async def _fact(self, chat_id, args) -> CommandResponse:
    facts_user_handle = args[0]
    facts = " ".join(args[1:])
    try:
        self.db.add_fact(chat_id, facts_user_handle, facts)
        return CommandResponse("fact_added", {"user_handle": facts_user_handle})
    except ValueError as e:
        self.logger.error(f"Error adding fact: {e}")
        return CommandResponse("inappropriate_fact", {}, None)
