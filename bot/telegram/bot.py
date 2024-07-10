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
    ContextTypes,
)
from telegram.constants import ParseMode

import logging
from functools import partial

from .utils import get_context, get_person, get_message, get_args
from .keyboards import get_paginated_list_keyboard


from ..models.base_bot import BaseBot
from ..models.localizer import Localizer
from ..models.config import TGConfig
from ..models.base_handlers import BaseHandler


class TelegramBot:
    def __init__(
        self,
        telegram_token: str,
        bot: BaseBot,
        telegram_bot_config: TGConfig,
    ):
        self.telegram_token = telegram_token
        self.telegram_bot_config = telegram_bot_config
        self.commands = bot.get_commands()
        self.messages = bot.get_messages()
        self.callbacks = bot.get_callbacks()
        self.logger = logging.getLogger("TelegramBot")

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=command.get_localized_description(),
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
            CommandHandler(command.command, partial(self.handle, bot_handler=command))
            for command in sorted(self.commands, key=lambda x: x.list_priority_order)
        ]
        message_handlers = [
            MessageHandler(
                (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND,
                partial(self.handle, bot_handler=message),
            )
            for message in self.messages
        ]
        callback_handlers = [
            CallbackQueryHandler(
                partial(self.handle, bot_handler=callback),
                "^" + callback.callback_action,
            )
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

    async def handle(
        self, update: Update, context: CallbackContext, bot_handler: BaseHandler
    ) -> None:
        """
        Handles the update and sends the response back to the user.
        """
        handler_context = await get_context(update, context)
        handler_person = await get_person(update, context)
        handler_message = await get_message(update, context)
        handler_args = await get_args(update, context)

        result = await bot_handler.handle(
            person=handler_person,
            context=handler_context,
            message=handler_message,
            args=handler_args,
        )
        if result is None:
            return
        text_response = self.localizer.get_command_response(result.text, result.kwargs)

        await self.send_message(
            context=context,
            chat_id=update.effective_chat.id,
            text=text_response,
            reply_message_id=update.effective_message.message_id,
            thread_id=handler_context.thread_id,
            parse_mode=ParseMode.HTML,
            keyboard=result.keyboard,
        )

    async def send_message(
        self,
        context,
        chat_id,
        text,
        image_url=None,
        reply_message_id=None,
        thread_id=None,
        parse_mode=ParseMode.HTML,
        keyboard=None,
    ) -> None:
        if keyboard:
            markup = get_paginated_list_keyboard(
                value_id_to_name=keyboard.modes_dict,
                callback=keyboard.callback,
                button_action=keyboard.button_action,
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
                reply_markup=markup,
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
            )
