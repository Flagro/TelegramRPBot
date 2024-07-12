from typing import List

from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message, TranscribedMessage
from ..auth import AllowedUser
from typing import Optional


class MessageHandler(BaseMessageHandler):
    permissions = [AllowedUser]

    async def get_reply(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> Optional[CommandResponse]:
        conversation_tracker_enabled = await self.db.get_conversation_tracker_state(context)
        if not conversation_tracker_enabled and not context.is_bot_mentioned:
            return None
        # Note that here the responsibility to pass NULL images and Audio is on the
        # outer level bot processing (TG bot or other bot)
        image_description = await self.ai.describe_image(message.in_file_image) if message.in_file_image else None
        voice_description = await self.ai.transcribe_audio(message.in_file_audio) if message.in_file_audio else None
        user_input = self.localizer.compose_user_input(
            message, image_description, voice_description
        )
        await self.db.add_user_message_to_dialog(context, person, user_input)
        if not context.is_bot_mentioned:
            return None
        response_message, response_image_url = await self.ai.get_reply(
            user_input
        )
        await self.db.add_bot_response_to_dialog(
            context, response_message, response_image_url
        )
        return CommandResponse("message_response", {"response_text": response_message})
