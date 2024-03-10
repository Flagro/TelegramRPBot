from telegram import Update, BotCommand
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    Application,
)
from telegram.constants import ParseMode

import io
import traceback
import html
import json
import logging
from collections import namedtuple
from functools import wraps
from inspect import signature


def authorized(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_handle = update.message.from_user.username
        if "@" + user_handle not in self.allowed_handles:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=self._localized_text(
                    update.message.chat_id, "unauthorized_command"
                ),
            )
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
        is_private_chat = update.message.chat.type == "private"
        is_bot_mentioned = (
            update.message.text is not None
            and ("@" + context.bot.username) in update.message.text
        )
        bot_in_reply_tree = (
            update.message.reply_to_message is not None
            and update.message.reply_to_message.from_user.id == context.bot.id
        )
        if not (is_private_chat or bot_in_reply_tree or is_bot_mentioned):
            return
        user_handle = "@" + update.message.from_user.username
        chat_id = update.message.chat_id
        reply_message_id = update.message.message_id
        thread_id = None
        if update.effective_message and update.effective_message.is_topic_message:
            thread_id = update.effective_message.message_thread_id
        message = update.message.text
        # get image and audio in memory
        if update.message.photo:
            photo_file = await context.bot.getFile(update.message.photo[-1].file_id)
            image_stream = io.BytesIO()
            await photo_file.download(out=image_stream)
            image_stream.seek(0)
            image = image_stream
        else:
            image = None

        if update.message.voice:
            voice_file = await context.bot.getFile(update.message.voice.file_id)
            voice_stream = io.BytesIO()
            await voice_file.download(out=voice_stream)
            voice_stream.seek(0)
            audio = voice_stream
        else:
            audio = None

        return await func(
            self,
            user_handle,
            chat_id,
            reply_message_id,
            thread_id,
            message,
            image,
            audio,
        )

    return wrapper


class TelegramRPBot:
    def __init__(
        self,
        telegram_token,
        allowed_handles,
        admin_handles,
        db,
        ai,
        localizer,
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

    async def post_init(self, application: Application):
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=self.localizer.get(command.description_tag),
            )
            for command in self.commands
        ]
        await application.bot.set_my_commands(bot_commands)

    def run(self):
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
        application.add_handlers(command_handlers + message_handlers)
        application.add_error_handler(self.error_handle)
        application.run_polling()

    async def send_message(self, chat_id, text, parse_mode=ParseMode.HTML):
        self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

    async def error_handle(self, update: Update, context: CallbackContext) -> None:
        self.logger.error(msg="Exception while handling an update:", exc_info=context.error)
        try:
            # collect error message
            tb_list = traceback.format_exception(
                None, context.error, context.error.__traceback__
            )
            tb_string = "".join(tb_list)
            update_str = update.to_dict() if isinstance(update, Update) else str(update)
            message = (
                f"An exception was raised while handling an update\n"
                f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
                "</pre>\n\n"
                f"<pre>{html.escape(tb_string)}</pre>"
            )
            # log the error message
        except:
            # log the exception in error handler
            pass

    @command_handler
    @authorized(["bot_admin", "group_admin", "group_owner"])
    async def _reset(self, chat_id, user_handle):
        pass

    @command_handler
    @authorized
    async def _mode(self, chat_id, user_handle, args):
        pass

    @command_handler
    @authorized
    async def _addmode(self, chat_id, user_handle, args):
        pass

    @command_handler
    @authorized
    async def _deletemode(self, chat_id, user_handle, args):
        pass

    @command_handler
    @authorized
    async def _introduce(self, chat_id, user_handle, args):
        pass

    @command_handler
    @authorized
    async def _fact(self, chat_id, user_handle, args):
        pass

    @command_handler
    @authorized
    async def _clearfacts(self, chat_id, user_handle):
        pass

    @command_handler
    @authorized
    async def _usage(self, chat_id, user_handle):
        pass

    @command_handler
    @authorized
    async def _language(self, chat_id, user_handle, args):
        pass

    @command_handler
    async def _help(self, chat_id, user_handle):
        pass

    @message_handler
    @authorized
    async def _get_reply(
        self, chat_id, user_handle, reply_message_id, thread_id, message, image, audio
    ):
        pass
