from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from functools import wraps
from inspect import signature

from .utils import bot_mentioned, get_file_in_memory


def authorized(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_handle = "@" + update.message.from_user.username
        if user_handle not in self.allowed_handles:
            # TODO: log unauthorized access
            return
        return await func(self, update, context)

    return wrapper


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
        return await func(self, **params)

    return wrapper


def message_handler(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not bot_mentioned(update, context):
            return
        user_handle = "@" + update.message.from_user.username
        chat_id = update.message.chat_id
        reply_message_id = update.message.message_id
        thread_id = None
        if update.effective_message and update.effective_message.is_topic_message:
            thread_id = update.effective_message.message_thread_id
        message = update.message.text
        
        # get image and audio in memory
        image = None
        if update.message.photo:
            image = get_file_in_memory(update.message.photo[-1].file_id, context)
        
        voice = None
        if update.message.voice:
            voice = get_file_in_memory(update.message.voice.file_id, context)

        return await func(
            self,
            user_handle,
            chat_id,
            reply_message_id,
            thread_id,
            message,
            image,
            voice,
        )

    return wrapper
