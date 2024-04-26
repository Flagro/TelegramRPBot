from ...models.base_handlers import BaseCallbackHandler


class CallbackHandler(BaseCallbackHandler):
    pattern = "^delete_chat_mode"
    
    async def handle(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.delete_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_deleted", {"mode_id": mode_id}, None)
