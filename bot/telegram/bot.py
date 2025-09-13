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
from typing import Literal, Optional, Tuple
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
        self.logger = logging.getLogger(self.__class__.__name__)

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
            .rate_limiter(
                AIORateLimiter(
                    max_retries=self.telegram_bot_config.rate_limiter_max_retries
                )
            )
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
        bot_input = await get_bot_input(update, context)
        await self.push_state(update, context, "sending_text")

        if bot_handler.streamable and self.telegram_bot_config.enable_message_streaming:
            first_message_id = None
            final_image_url = None
            final_keyboard = None
            last_sent_text = None  # Track last sent text to avoid duplicate edits

            async for result in buffer_streaming_response(
                bot_handler.stream_handle(
                    person=bot_input.person,
                    context=bot_input.context,
                    message=bot_input.message,
                    args=bot_input.args,
                ),
                is_group_chat(update=update),
            ):
                if result is not None:
                    # Track the final image and keyboard for sending after streaming
                    if result.image_url:
                        final_image_url = result.image_url
                    if result.keyboard:
                        final_keyboard = result.keyboard

                    # Stream only text updates (ignore image during streaming)
                    first_message_id, last_sent_text = await self.process_stream_result(
                        result, update, context, first_message_id, last_sent_text
                    )
                    await asyncio.sleep(
                        self.telegram_bot_config.stream_buffer_sleep_time
                    )

            # After streaming is complete, send image as separate message if needed
            if final_image_url:
                await self.send_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    text=None,
                    image_url=final_image_url,
                    reply_message_id=update.effective_message.message_id,
                    keyboard=final_keyboard,
                )
            # If no image but there's a final keyboard, update the last message
            elif final_keyboard and first_message_id:
                markup = get_paginated_list_keyboard(
                    value_id_to_name=final_keyboard.modes_dict,
                    callback=final_keyboard.callback,
                    button_action=final_keyboard.button_action,
                )
                await context.bot.edit_message_reply_markup(
                    chat_id=update.effective_chat.id,
                    message_id=first_message_id,
                    reply_markup=markup,
                )
        else:
            result = await bot_handler.handle(
                person=bot_input.person,
                context=bot_input.context,
                message=bot_input.message,
                args=bot_input.args,
            )
            if result is not None:
                await self.process_result(result, update, context)

    async def process_stream_result(
        self,
        result: LocalizedCommandResponse,
        update: Update,
        context: CallbackContext,
        first_message_id: Optional[str],
        last_sent_text: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        latest_text_response = result.localized_text

        # Only process text updates during streaming (ignore images and keyboards)
        if latest_text_response:
            if first_message_id is None:
                # Send initial text message (without image/keyboard for streaming)
                message = await self.send_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    text=latest_text_response,
                    image_url=None,  # No image during streaming
                    reply_message_id=update.effective_message.message_id,
                    keyboard=None,  # No keyboard during streaming
                )
                return message.message_id, latest_text_response
            else:
                # Only update if text content has actually changed
                if latest_text_response != last_sent_text:
                    try:
                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=first_message_id,
                            text=latest_text_response,
                            reply_markup=None,  # No keyboard during streaming
                        )
                        return first_message_id, latest_text_response
                    except Exception as e:
                        self.logger.debug(f"Message edit failed: {e}")
                        return first_message_id, last_sent_text
                else:
                    # Content is the same, no need to update
                    return first_message_id, last_sent_text
        return first_message_id, last_sent_text

    async def process_result(
        self,
        result: LocalizedCommandResponse,
        update: Update,
        context: CallbackContext,
    ) -> str:
        message = await self.send_message(
            context=context,
            chat_id=update.effective_chat.id,
            text=result.localized_text,
            image_url=result.image_url,
            reply_message_id=update.effective_message.message_id,
            keyboard=result.keyboard,
        )
        return message.message_id

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
        markup = (
            None
            if not keyboard
            else get_paginated_list_keyboard(
                value_id_to_name=keyboard.modes_dict,
                callback=keyboard.callback,
                button_action=keyboard.button_action,
            )
        )

        # If there's an image URL, send photo with caption
        if image_url:
            return await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=text,
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
                reply_markup=markup,
            )
