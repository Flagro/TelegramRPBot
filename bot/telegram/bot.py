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
    get_bot_input,
    buffer_streaming_response,
    is_group_chat,
)
from .keyboards import get_paginated_list_keyboard

from ..models.base_bot import BaseBot
from ..models.config import TGConfig
from ..models.base_handlers import BaseHandler
from ..models.handlers_response import KeyboardResponse
from ..models.handlers_input import BotInput
from ..models.handlers_response import LocalizedCommandResponse


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
        bot_input = get_bot_input(update, context)
        await self.push_state(update, context, "sending_text")

        if bot_handler.streamable and self.telegram_bot_config.enable_message_streaming:
            first_message_id = None
            async for result in buffer_streaming_response(
                bot_handler.stream_handle(
                    person=bot_input.person,
                    context=bot_input.context,
                    message=bot_input.message,
                    args=bot_input.args,
                ),
                is_group_chat(update=update),
            ):
                first_message_id = await self.process_stream_result(
                    result, update, context, first_message_id, bot_input
                )
                await asyncio.sleep(self.telegram_bot_config.stream_buffer_sleep_time)
        else:
            result = await bot_handler.handle(
                person=bot_input.person,
                context=bot_input.context,
                message=bot_input.message,
                args=bot_input.args,
            )
            if result is not None:
                await self.process_result(result, update, context, bot_input)

    async def process_stream_result(
        self,
        result: LocalizedCommandResponse,
        update: Update,
        context: CallbackContext,
        first_message_id: str,
        bot_input: BotInput,
    ) -> Optional[int]:
        latest_text_response = result.localized_text

        if latest_text_response:
            if first_message_id is None:
                message = await self.send_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    text=latest_text_response,
                    reply_message_id=update.effective_message.message_id,
                    parse_mode=ParseMode.HTML,
                    keyboard=result.keyboard,
                )
                first_message_id = message.message_id
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=first_message_id,
                    text=latest_text_response,
                    parse_mode=ParseMode.HTML,
                    reply_markup=result.keyboard,
                )
        elif result.keyboard:
            await self.send_message(
                context=context,
                chat_id=update.effective_chat.id,
                text=latest_text_response or "",
                reply_message_id=first_message_id
                or update.effective_message.message_id,
                parse_mode=ParseMode.HTML,
                keyboard=result.keyboard,
            )
        return first_message_id

    async def process_result(
        self,
        result: LocalizedCommandResponse,
        update: Update,
        context: CallbackContext,
        bot_input: BotInput,
    ) -> None:
        text_response = result.localized_text
        await self.send_message(
            context=context,
            chat_id=update.effective_chat.id,
            text=text_response,
            reply_message_id=update.effective_message.message_id,
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
        parse_mode: ParseMode = ParseMode.HTML,
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
        elif image_url:
            return await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
            )
        else:
            return await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_message_id,
                parse_mode=parse_mode,
            )
