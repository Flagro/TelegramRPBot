from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import BadRequest

from inspect import signature

from .utils import bot_mentioned, get_file_in_memory, get_context, get_person, get_message


def callback_wrapper(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        sig = signature(func)
        params = {}
        if "context" in sig.parameters:
            params["context"] = get_context(update, context)
        if "person" in sig.parameters:
            params["person"] = get_person(update, context)
        if "args" in sig.parameters:
            params["callback_args"] = query.data.split("|")[1:]

        result = await func(self, **params)
        text_response, parse_mode = self.localizer.get_command_response(
            result.text, result.kwargs
        )

        try:
            await query.edit_message_text(
                text_response, reply_markup=result.markup, parse_mode=parse_mode
            )
        except BadRequest as e:
            if not str(e).startswith("Message is not modified"):
                self.logger.error(f"Error editing message: {e}")
    return wrapper


def message_wrapper(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        rp_person = get_person(update, context)
        rp_context = get_context(update, context)
        rp_message = get_message(update, context)

        return await func(
            self,
            rp_person,
            rp_context,
            rp_message,
        )
    return wrapper


def command_wrapper(func):
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
