from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, BotAdmin
from typing import Optional, AsyncIterator, List
from datetime import datetime


class MessageHandler(BaseMessageHandler):
    permissions = [AllowedUser, BotAdmin]

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
        conversation_tracker_enabled = await self.db.chats.get_conversation_tracker_state(
            context
        )
        chat_is_started = await self.db.chats.chat_is_started(context)
        if not chat_is_started or (
            not conversation_tracker_enabled and not context.is_bot_mentioned
        ):
            return
        user_input = await self._get_user_input(message)
        await self.db.dialogs.add_user_message_to_dialog(context, person, user_input, message.timestamp)
        if not context.is_bot_mentioned:
            return None
        # Take everything besides the last one since the last one is the current message
        messages_history = self.db.dialogs.get_messages(context, last_n=15)[0:-1]
        prompt = await self.localizer.compose_prompt(user_input, messages_history)
        response_message = await self.ai.get_reply(prompt)
        await self.db.dialogs.add_bot_response_to_dialog(context, response_message, datetime.now())
        return CommandResponse("message_response", {"response_text": response_message})

    async def stream_get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        conversation_tracker_enabled = await self.db.chats.get_conversation_tracker_state(
            context
        )
        chat_is_started = await self.db.chats.chat_is_started(context)
        if not chat_is_started or (
            not conversation_tracker_enabled and not context.is_bot_mentioned
        ):
            return
        user_input = await self._get_user_input(message)
        await self.db.dialogs.add_user_message_to_dialog(context, person, user_input, message.timestamp)
        if not context.is_bot_mentioned:
            return
        # Take everything besides the last one since the last one is the current message
        messages_history = self.db.dialogs.get_messages(context, last_n=15)[0:-1]
        prompt = await self.localizer.compose_prompt(user_input, messages_history)
        response_message = ""
        async for response_message_chunk in self.ai.get_streaming_reply(prompt):
            if not response_message_chunk:
                continue
            response_message += response_message_chunk
            yield CommandResponse(
                "streaming_message_response", {"response_text": response_message}
            )
        await self.db.dialogs.add_bot_response_to_dialog(context, response_message, datetime.now())
