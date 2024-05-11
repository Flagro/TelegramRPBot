from telegram import Update, BotCommand
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    Application,
)
from telegram.constants import ParseMode

import logging
from collections import namedtuple
from typing import List, Optional

from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import BadRequest

from functools import wraps
from inspect import signature

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from typing import List, Optional


from __future__ import annotations

import io
import asyncio
import logging

from typing import List

import telegram
from telegram import Update, constants
from telegram.ext import CallbackContext, ContextTypes


from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps


def authorized(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_handle = "@" + update.message.from_user.username
        self.db.create_user_if_not_exists(user_handle)
        if user_handle not in self.allowed_handles:
            # TODO: log unauthorized access
            return
        return await func(self, update, context)

    return wrapper


def bot_mentioned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    is_private_chat = update.message.chat.type == "private"
    is_bot_mentioned = (
        update.message.text is not None
        and ("@" + context.bot.username) in update.message.text
    )
    bot_in_reply_tree = (
        update.message.reply_to_message is not None
        and update.message.reply_to_message.from_user.id == context.bot.id
    )
    return not (is_private_chat or bot_in_reply_tree or is_bot_mentioned)


def get_messages_tree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    messages = [update.message.text]
    current_message = update.message
    while current_message.reply_to_message:
        current_message = current_message.reply_to_message
        messages.append(current_message.text)
    return messages


async def get_file_in_memory(
    file_id: str, context: ContextTypes.DEFAULT_TYPE
) -> io.BytesIO:
    file = await context.bot.getFile(file_id)
    file_stream = io.BytesIO()
    await file.download(out=file_stream)
    file_stream.seek(0)
    return file_stream


def get_thread_id(update: Update) -> int | None:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def get_stream_cutoff_values(content: str) -> int:
    """
    Gets the stream cutoff values for the message length
    """
    if len(content) > 1000:
        return 180
    elif len(content) > 200:
        return 120
    elif len(content) > 50:
        return 90
    else:
        return 50


async def wrap_with_indicator(
    update: Update,
    context: CallbackContext,
    coroutine,
    chat_action: constants.ChatAction = "",
    is_inline=False,
):
    """
    Wraps a coroutine while repeatedly sending a chat action to the user.
    """
    task = context.application.create_task(coroutine(), update=update)
    while not task.done():
        if not is_inline:
            context.application.create_task(
                update.effective_chat.send_action(
                    chat_action, message_thread_id=get_thread_id(update)
                )
            )
        try:
            await asyncio.wait_for(asyncio.shield(task), 4.5)
        except asyncio.TimeoutError:
            pass


# TODO: adapt tenacity here
async def edit_message_with_retry(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int | None,
    message_id: str,
    text: str,
    markdown: bool = True,
    is_inline: bool = False,
):
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=int(message_id) if not is_inline else None,
            inline_message_id=message_id if is_inline else None,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN if markdown else None,
        )
    except telegram.error.BadRequest as e:
        if str(e).startswith("Message is not modified"):
            return
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=int(message_id) if not is_inline else None,
                inline_message_id=message_id if is_inline else None,
                text=text,
            )
        except Exception as e:
            logging.warning(f"Failed to edit message: {str(e)}")
            raise e

    except Exception as e:
        logging.warning(str(e))
        raise e


def get_chat_modes_keyboard(
    chat_modes: List[ChatModeResponse],
    callback: str,
    button_action: str,
    page_index: Optional[int] = 0,
    modes_per_page: Optional[int] = 5,
) -> InlineKeyboardMarkup:
    page_start = page_index * modes_per_page
    page_end = (page_index + 1) * modes_per_page

    # chat modes
    modes = []
    for chat_mode in chat_modes[page_start:page_end]:
        modes.append(
            InlineKeyboardButton(
                chat_mode.mode_name, callback_data=f"{button_action}|{chat_mode.id}"
            )
        )

    # pagination
    pagination = []
    if page_start > 0:
        pagination.append(
            InlineKeyboardButton(
                "«", callback_data=f"{callback}|{button_action}|{page_index - 1}"
            )
        )
    if page_end < len(chat_modes):
        pagination.append(
            InlineKeyboardButton(
                "»", callback_data=f"{callback}|{button_action}|{page_index + 1}"
            )
        )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup


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


def callback_handler(func):
    @wraps(func)
    async def wrapper(self, update: Update, _: CallbackContext):
        query = update.callback_query
        await query.answer()

        sig = signature(func)
        params = {}
        if "user_handle" in sig.parameters:
            params["user_handle"] = update.callback_query.from_user.username
        if "chat_id" in sig.parameters:
            params["chat_id"] = update.callback_query.message.chat.id
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


def message_handler(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        return await func(
            self,
            chat_id,
            thread_id,
            bot_mentioned(update, context),
            user_handle,
            message,
            image,
            voice,
        )

    return wrapper


CommandResponse = namedtuple("CommandResponse", ["text", "kwargs", "markup"])
MessageResponse = namedtuple("MessageResponse", ["text", "image_url"])


class TelegramRPBot:
    def __init__(
        self,
        telegram_token: str,
        allowed_handles: List[str],
        admin_handles: List[str],
        db: DB,
        ai: AI,
        localizer: Localizer,
    ):
        self.telegram_token = telegram_token
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

        # Define bot commands
        Command = namedtuple("Command", ["command", "description_tag", "handler"])
        self.commands = [
            Command("reset", "reset_description", self._reset),
            Command("mode", "mode_description", self._mode),
            Command("addmode", "addmode_description", self._addmode),
            Command("deletemode", "deletemode_description", self._deletemode),
            Command("introduce", "introduce_description", self._introduce),
            Command("fact", "fact_description", self._fact),
            Command("clearfacts", "clearfacts_description", self._clearfacts),
            Command("usage", "usage_description", self._usage),
            Command("language", "language_description", self._language),
            Command("help", "help_description", self._help),
        ]
        Handler = namedtuple("Handler", ["filters", "handler"])
        self.handlers = [
            Handler(
                (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND,
                self._get_reply,
            ),
        ]
        Callback = namedtuple("Callbacks", ["pattern", "callback"])
        self.callbacks = [
            Callback("^show_chat_modes", self._show_chat_modes),
            Callback("^set_chat_mode", self._set_chat_mode),
            Callback("^delete_chat_mode", self._delete_chat_mode),
        ]

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=self.localizer.get_command_response(
                    command.description_tag
                ),
            )
            for command in self.commands
        ]
        await application.bot.set_my_commands(bot_commands)

    def run(self) -> None:
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """
        application = (
            ApplicationBuilder()
            .token(self.telegram_token)
            .concurrent_updates(True)
            .rate_limiter(AIORateLimiter(max_retries=5))
            .post_init(self.post_init)
            .build()
        )
        command_handlers = [
            CommandHandler(command.command, command.handler)
            for command in self.commands
        ]
        message_handlers = [
            MessageHandler(handler.filters, handler.handler)
            for handler in self.handlers
        ]
        callback_handlers = [
            CallbackQueryHandler(callback.callback, callback.pattern)
            for callback in self.callbacks
        ]
        application.add_handlers(
            command_handlers + message_handlers + callback_handlers
        )
        application.add_error_handler(self.error_handle)
        application.run_polling()

    async def error_handle(self, update: Update, context: CallbackContext) -> None:
        self.logger.error(
            msg="Exception while handling an update:", exc_info=context.error
        )

    async def send_message(
        self,
        chat_id,
        text,
        image_url=None,
        reply_message_id=None,
        thread_id=None,
        parse_mode=ParseMode.HTML,
    ) -> None:
        self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_message_id,
            parse_mode=parse_mode,
        )

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

    @callback_handler
    @authorized
    async def _set_chat_mode(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.set_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_set", {"mode_id": mode_id}, None)

    @callback_handler
    @authorized
    async def _delete_chat_mode(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.delete_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_deleted", {"mode_id": mode_id}, None)

    @command_handler
    @authorized
    async def _mode(self, chat_id) -> CommandResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", "set_chat_mode"
        )
        return CommandResponse("choose_mode", {}, modes_keyboard)

    @command_handler
    @authorized
    async def _addmode(self, chat_id, args) -> CommandResponse:
        mode_description = " ".join(args)
        # Get the first sentence or paragraph of the mode description:
        # TODO: implement NER here
        mode_name = mode_description.split("\n")[0].split(".")[0]
        try:
            self.db.add_chat_mode(chat_id, mode_name, mode_description)
            return CommandResponse("mode_added", {"mode_name": mode_name})
        except ValueError as e:
            self.logger.error(f"Error adding mode: {e}")
            return CommandResponse("inappropriate_mode", {}, None)

    @command_handler
    @authorized
    async def _deletemode(self, chat_id) -> CommandResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", "delete_chat_mode"
        )
        return CommandResponse("choose_mode_to_delete", {}, modes_keyboard)

    @command_handler
    @authorized
    async def _introduce(self, chat_id, user_handle, args) -> CommandResponse:
        introduction = " ".join(args)
        try:
            self.db.add_introduction(chat_id, user_handle, introduction)
            return CommandResponse("introduction_added", {"user_handle": user_handle})
        except ValueError as e:
            self.logger.error(f"Error adding introduction: {e}")
            return CommandResponse("inappropriate_introduction", {}, None)

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

    @command_handler
    @authorized
    async def _clearfacts(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        self.db.clear_facts(chat_id, facts_user_handle)
        return CommandResponse(
            "facts_cleared", {"user_handle": facts_user_handle}, None
        )

    @command_handler
    @authorized
    async def _usage(self, user_handle) -> CommandResponse:
        user_usage = self.db.get_user_usage(user_handle)
        return CommandResponse("usage_text", user_usage._asdict(), None)

    @command_handler
    @authorized
    async def _language(self, chat_id, args) -> CommandResponse:
        language = args[0]
        try:
            self.localizer.set_language(chat_id, language)
            return CommandResponse("language_set", {"language": language})
        except ValueError as e:
            self.logger.error(f"Error setting language: {e}")
            return CommandResponse("language_set_error", {"language": language}, None)

    @command_handler
    @authorized
    async def _reset(self, chat_id) -> CommandResponse:
        self.db.reset(chat_id)
        return CommandResponse("reset_done", {}, None)

    @command_handler
    async def _help(self) -> CommandResponse:
        return CommandResponse("help_text", {}, None)

    @message_handler
    @authorized
    async def _get_reply(
        self, chat_id, thread_id, is_bot_mentioned, user_handle, message, image, voice
    ) -> Optional[MessageResponse]:
        if self.telegram_bot_config.track_conversation_thread:
            self.db.save_thread_message(thread_id, user_handle, message)
        if not is_bot_mentioned:
            return None

        image_description = None
        if image:
            image_description = await self.ai.describe_image(image)
        voice_description = None
        if voice:
            voice_description = await self.ai.transcribe_audio(voice)
        self.db.add_user_input_to_dialog(
            chat_id, user_handle, message, image_description, voice_description
        )
        user_input = self.localizer.compose_user_input(
            message, image_description, voice_description
        )
        response_message, response_image_url = await self.ai.get_reply(
            chat_id, thread_id, user_handle, user_input
        )
        self.db.add_bot_response_to_dialog(
            chat_id, response_message, response_image_url
        )
        return MessageResponse(response_message, response_image_url)
