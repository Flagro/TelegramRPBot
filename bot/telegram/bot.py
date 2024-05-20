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
from ..models.base_bot import BaseBot
from ..models.config import TGConfig
from .wrappers import command_wrapper, message_wrapper, callback_wrapper


class TelegramBot:
    def __init__(
        self,
        telegram_token: str,
        bot: BaseBot,
        telegram_config: TGConfig,
    ):
        self.telegram_token = telegram_token
        self.commands = bot.get_commands()
        self.messages = bot.get_messages()
        self.callbacks = bot.get_callbacks()

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=self.localizer.get_command_response(command.description_tag),
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
            CommandHandler(command.command, command_wrapper(command.handler))
            for command in self.commands
        ]
        message_handlers = [
            MessageHandler(message.filters, message_wrapper(message.handler))
            for message in self.messages
        ]
        callback_handlers = [
            CallbackQueryHandler(callback_wrapper(callback.handler), "^" + callback.callback_action)
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
