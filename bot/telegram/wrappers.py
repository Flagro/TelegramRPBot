from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import BadRequest

from inspect import signature

from ..utils import bot_mentioned, get_file_in_memory


async def callback_wrapper(self, update: Update, _: CallbackContext):
    query = update.callback_query
    await query.answer()

    sig = signature(self.handle)
    params = {}
    if "user_handle" in sig.parameters:
        params["user_handle"] = update.callback_query.from_user.username
    if "chat_id" in sig.parameters:
        params["chat_id"] = update.callback_query.message.chat.id
    if "args" in sig.parameters:
        params["callback_args"] = query.data.split("|")[1:]

    result = await self.handle(self, **params)
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


async def message_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_handle = "@" + update.message.from_user.username
    chat_id = update.message.chat_id
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

    return await self.handle(
        self,
        chat_id,
        thread_id,
        bot_mentioned(update, context),
        user_handle,
        message,
        image,
        voice,
    )


async def command_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    sig = signature(self.handle)
    params = {}
    if "user_handle" in sig.parameters:
        params["user_handle"] = update.effective_user.username
    if "chat_id" in sig.parameters:
        params["chat_id"] = update.effective_chat.id
    if "args" in sig.parameters:
        params["command_args"] = context.args
    result = await self.handle(self, **params)
    text_response, parse_mode = self.localizer.get_command_response(
        result.text, result.kwargs
    )

    self.send_message(
        chat_id=update.effective_chat.id,
        text=text_response,
        parse_mode=parse_mode,
    )
