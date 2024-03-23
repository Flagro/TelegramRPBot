from telegram import Update, BotCommand
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
)
from telegram.constants import ParseMode

import logging
from collections import namedtuple

from .decorators import authorized, command_handler, message_handler


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

        self.CommandResponse = namedtuple("CommandResponse", ["text", "kwargs"])
        self.MessageResponse = namedtuple("MessageResponse", ["text", "image_url"])

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
    ):
        self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_message_id,
            parse_mode=parse_mode,
        )

    @command_handler
    @authorized
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
    async def _help(self):
        return self.CommandResponse("help_text", {})

    @message_handler
    @authorized
    async def _get_reply(self, chat_id, user_handle, message, image, voice):
        image_description = None
        if image:
            image_description = await self.ai.describe_image(image)
        voice_description = None
        if voice:
            voice_description = await self.ai.transcribe_audio(voice)
        user_input = self.localizer.compose_user_input(
            message, image_description, voice_description
        )
        response_message, response_image_url = await self.ai.get_reply(chat_id, user_handle, user_input)
        return self.MessageResponse(response_message, response_image_url)
