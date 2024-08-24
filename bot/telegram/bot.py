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
import asyncio
from typing import Literal, Optional
from functools import partial

from .utils import (
    get_context,
    get_person,
    get_message,
    get_args,
    buffer_streaming_response,
    is_group_chat,
)
from .keyboards import get_paginated_list_keyboard

from ..models.base_bot import BaseBot
from ..models.config import TGConfig
from ..models.base_handlers import BaseHandler
from ..models.handlers_response import KeyboardResponse


class TelegramBot:
    def __init__(
        self,
        telegram_token: str,
        bot: BaseBot,
        telegram_bot_config: TGConfig,
    ):
        self.telegram_token = telegram_token
        self.telegram_bot_config = telegram_bot_config
        self.commands = bot.commands
        self.messages = bot.messages
        self.callbacks = bot.callbacks
        self.logger = logging.getLogger("TelegramBot")

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=await command.get_localized_description(),
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
            for command in sorted(
                self.commands, key=lambda x: (x.list_priority_order, x.command)
            )
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

        if bot_handler.streamable and self.telegram_bot_config.enable_message_streaming:
            first_message_id = None
            async for result in buffer_streaming_response(
                bot_handler.stream_handle(
                    person=handler_person,
                    context=handler_context,
                    message=handler_message,
                    args=handler_args,
                ),
                is_group_chat(update=update),
            ):
                latest_text_response = result.localized_text
                await self.push_state(update, context, "sending_text")
                if latest_text_response and first_message_id is None:
                    message = await self.send_message(
                        context=context,
                        chat_id=update.effective_chat.id,
                        text=latest_text_response,
                        reply_message_id=update.effective_message.message_id,
                        thread_id=handler_context.thread_id,
                        parse_mode=ParseMode.HTML,
                        keyboard=result.keyboard,
                    )
                    first_message_id = message.message_id
                elif latest_text_response and first_message_id is not None:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=first_message_id,
                        text=latest_text_response,
                        parse_mode=ParseMode.HTML,
                        reply_markup=result.keyboard,
                    )
                elif latest_text_response is None and result.keyboard is not None:
                    await self.send_message(
                        context=context,
                        chat_id=update.effective_chat.id,
                        text=latest_text_response,
                        reply_message_id=first_message_id,
                        thread_id=handler_context.thread_id,
                        parse_mode=ParseMode.HTML,
                        keyboard=result.keyboard,
                    )
                await asyncio.sleep(0.5)
        else:
            result = await bot_handler.handle(
                person=handler_person,
                context=handler_context,
                message=handler_message,
                args=handler_args,
            )
            if result is None:
                return
            text_response = result.localized_text

            await self.push_state(update, context, "sending_text")
            await self.send_message(
                context=context,
                chat_id=update.effective_chat.id,
                text=text_response,
                reply_message_id=update.effective_message.message_id,
                thread_id=handler_context.thread_id,
                parse_mode=ParseMode.HTML,
                keyboard=result.keyboard,
            )

    async def push_state(
        self,
        update: Update,
        context: CallbackContext,
        state: Literal["sending_text", "sending_image", "sending_audio"],
    ) -> None:
        action_map = {
            "sending_text": "typing",
            "sending_image": "upload_photo",
            "sending_audio": "upload_audio",
        }
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=action_map[state],
        )

    async def send_message(
        self,
        context: CallbackContext,
        chat_id: int,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        reply_message_id: Optional[int] = None,
        thread_id: Optional[int] = None,
        parse_mode: Optional[ParseMode] = ParseMode.HTML,
        keyboard: Optional[KeyboardResponse] = None,
    ) -> None:
        if keyboard:
            markup = get_paginated_list_keyboard(
                value_id_to_name=keyboard.modes_dict,
                callback=keyboard.callback,
                button_action=keyboard.button_action,
            )
            return await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
                reply_markup=markup,
            )
        else:
            return await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
            )
