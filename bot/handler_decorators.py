

def command_handler(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sig = signature(func)
        params = {}
        if "user_handle" in sig.parameters:
            params["user_handle"] = update.effective_user.username
        if "chat_id" in sig.parameters:
            params["chat_id"] = update.effective_chat.id
        if "args" in sig.parameters:
            params["command_args"] = context.args
        result = await func(self, **params)
        text_response, parse_mode = self.localizer.get_command_response(
            result.text, result.kwargs
        )

        self.send_message(
            chat_id=update.effective_chat.id,
            text=text_response,
            parse_mode=parse_mode,
        )

    return wrapper
