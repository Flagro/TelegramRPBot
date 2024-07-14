from typing import AsyncIterator, List

from bot.models.handlers_response import CommandResponseChunk

from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import CommandResponse, CommandResponseChunk
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser
from typing import Optional


class MessageHandler(BaseMessageHandler):
    permissions = [AllowedUser]

    async def _get_user_input(self, message: Message) -> str:
        # Note that here the responsibility to pass NULL images and Audio is on the
        # outer level bot processing (TG bot or other bot)
        image_description = (
            await self.ai.describe_image(message.in_file_image)
            if message.in_file_image
            else None
        )
        voice_description = (
            await self.ai.transcribe_audio(message.in_file_audio)
            if message.in_file_audio
            else None
        )
        user_input = self.localizer.compose_user_input(
            message.message_text, image_description, voice_description
        )
        return user_input

    async def get_reply(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> Optional[CommandResponse]:
        conversation_tracker_enabled = await self.db.get_conversation_tracker_state(
            context
        )
        if not conversation_tracker_enabled and not context.is_bot_mentioned:
            return None
        user_input = await self._get_user_input(message)
        await self.db.add_user_message_to_dialog(context, person, user_input)
        if not context.is_bot_mentioned:
            return None
        response_message = self.ai.get_reply(user_input)
        await self.db.add_bot_response_to_dialog(context, response_message, None)
        return CommandResponse("message_response", {})

    async def stream_get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponseChunk]:
        conversation_tracker_enabled = await self.db.get_conversation_tracker_state(
            context
        )
        if not conversation_tracker_enabled and not context.is_bot_mentioned:
            return None
        user_input = await self._get_user_input(message)
        await self.db.add_user_message_to_dialog(context, person, user_input)
        if not context.is_bot_mentioned:
            return None
        response_message = ""
        for response_message_chunk in self.ai.get_streaming_reply(user_input):
            yield CommandResponseChunk(
                response_message_chunk,
                "streaming_message_response",
                {},
            )
            response_message += response_message_chunk
        await self.db.add_bot_response_to_dialog(context, response_message, None)
