@callback_handler
@authorized
async def _show_chat_modes(self, chat_id, args) -> CommandResponse:
    button_action = args[0]
    page_index = int(args[1])
    available_modes = self.db.get_chat_modes(chat_id)
    modes_keyboard = get_chat_modes_keyboard(
        available_modes, "show_chat_modes", button_action, page_index
    )
    return CommandResponse("", {}, modes_keyboard)

pattern = "^show_chat_modes"
