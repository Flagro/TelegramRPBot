from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import MessageResponse
from typing import Optional

from telegram.ext import filters


class MessageHandler(BaseMessageHandler):
    permissions = []
    filters = (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND

    async def handle(
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
        self.db.add_bot_response_to_dialog(chat_id, response_message, response_image_url)
        return MessageResponse(response_message, response_image_url)
