from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, Application

from .utils import get_context, get_person, get_message, get_args


def handler_wrapper(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        handler_context = get_context(update, context)
        handler_person = get_person(update, context)
        handler_message = get_message(update, context)
        handler_args = get_args(update, context)

        result = await func(self, handler_person, handler_context, handler_args)
        text_response, parse_mode = self.localizer.get_command_response(
            result.text, result.kwargs
        )

        self.send_message(
            chat_id=update.effective_chat.id,
            text=text_response,
            parse_mode=parse_mode,
        )
    return wrapper
