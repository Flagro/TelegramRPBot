from typing import List

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
        args: List[str],
    ) -> Optional[CommandResponse]:
        if context.is_bot_mentioned:
            image_description = await self.ai.describe_image(message.in_file_image) if message.in_file_image else None
            voice_description = await self.ai.transcribe_audio(message.in_file_audio) if message.in_file_audio else None
            user_input = self.localizer.compose_user_input(
                message, image_description, voice_description
            )
            response_message, response_image_url = await self.ai.get_reply(
                user_input
            )
            await self.db.add_user_message_to_dialog(context, person, message.message_text)
            await self.db.add_bot_response_to_dialog(
                context, response_message, response_image_url
            )
        if await self.db.get_conversation_tracker_state(context):
            await self.db.add_user_message_to_dialog(context, person, message.message_text)
        return CommandResponse("message_response", {"response_text": response_message})
