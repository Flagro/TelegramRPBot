from abc import ABC, abstractmethod


class CallbackHandler(ABC):
    def __init__(self, db, ai, localizer):
        self.db = db
        self.ai = ai
        self.localizer = localizer

    def handle(self, update, context):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text="Selected option: {}".format(query.data))
        return self.bot.STATES.END


class MessageHandler(ABC):
    def __init__(self, db, ai, localizer):
        self.db = db
        self.ai = ai
        self.localizer = localizer

    def handle(self, update, context):
        message = update.message
        chat_id = message.chat_id
        user_handle = message.from_user.username
        message_text = message.text
        image = message.photo
        voice = message.voice
        is_bot_mentioned = message_text.startswith(f"@{context.bot.username}")
        thread_id = self.db.get_thread_id(chat_id, user_handle)
        return self._get_reply(
            chat_id, thread_id, is_bot_mentioned, user_handle, message_text, image, voice
        )

    @abstractmethod
    async def _get_reply(
        self, chat_id, thread_id, is_bot_mentioned, user_handle, message, image, voice
    ):
        pass
    
    
class CommandHandler(ABC):
    def __init__(self, db, ai, localizer):
        self.db = db
        self.ai = ai
        self.localizer = localizer

    def handle(self, update, context):
        message = update.message
        chat_id = message.chat_id
        user_handle = message.from_user.username
        command = message.text
        return self._get_reply(chat_id, user_handle, command)

    @abstractmethod
    async def _get_reply(self, chat_id, user_handle, command):
        pass
