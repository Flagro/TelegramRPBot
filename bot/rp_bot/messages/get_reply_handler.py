from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser
from typing import Optional


class MessageHandler(BaseMessageHandler):
    permissions = [AllowedUser]

    async def get_reply(
        self,
        person: Person,
        context: Context,
        message: Message,
    ) -> Optional[CommandResponse]:
        image = message.image
        voice = message.voice
        chat_id = context.chat_id
        thread_id = context.thread_id
        user_handle = person.user_handle
        track_conversation_thread = self.db.get_chat_mode(
            chat_id
        ).track_conversation_thread
        if track_conversation_thread:
            self.db.save_thread_message(thread_id, user_handle, message)
        if not context.is_bot_mentioned:
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
        return CommandResponse("message_response", {"response_text": response_message})
