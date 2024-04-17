@command_handler
@authorized
async def _deletemode(self, chat_id) -> CommandResponse:
    available_modes = self.db.get_chat_modes(chat_id)
    modes_keyboard = get_chat_modes_keyboard(
        available_modes, "show_chat_modes", "delete_chat_mode"
    )
    return CommandResponse("choose_mode_to_delete", {}, modes_keyboard)
