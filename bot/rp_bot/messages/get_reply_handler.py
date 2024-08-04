from ...models.base_handlers import BaseMessageHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import AllowedUser, BotAdmin, NotBanned
from typing import Optional, AsyncIterator, List
from datetime import datetime


class MessageHandler(BaseMessageHandler):
    permissions = [AllowedUser, BotAdmin, NotBanned]

    async def _estimate_reply_usage(self, context: Context, input_message: str) -> int:
        # Estimate the response based on amount of facts in the group chat,
        # the length of the message and wether or not it needs an image generation
        return len(input_message) // 10 + 1000 * ("image" in input_message)

    async def _get_user_usage(self, generated_message: str) -> int:
        return len(generated_message) // 10

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
        user_input = await self.localizer.compose_user_input(
            message.message_text, image_description, voice_description
        )
        return user_input

    async def _get_bot_output(self, response_message: str) -> str:
        localized_response = self.localizer.compose_bot_output(response_message)
        return localized_response

    async def prepare_get_reply(
        self,
        person: Person,
        context: Context,
        message: Message,
    ) -> Optional[str]:
        conversation_tracker_enabled = (
            await self.db.chats.get_conversation_tracker_state(context)
        )
        chat_is_started = await self.db.chats.chat_is_started(context)
        if not chat_is_started or (
            not conversation_tracker_enabled and not context.is_bot_mentioned
        ):
            return None
        user_input = await self._get_user_input(message)
        estimated_usage = await self._estimate_reply_usage(context, user_input)
        user_usage = await self.db.users.get_user_usage(person)
        user_limit = await self.db.users.get_user_usage_limit(person)
        if user_usage + estimated_usage > user_limit:
            self.logger.info(
                f"User {person.user_handle} exceeded the usage limit of {user_limit}"
            )
            return None
        await self.db.dialogs.add_message_to_dialog(
            context,
            person,
            user_input,
            message.timestamp,
        )
        if not context.is_bot_mentioned:
            return None
        # Take everything besides the last one since the last one is the current message
        messages_history = self.db.dialogs.get_messages(context, last_n=15)[0:-1]
        prompt = await self.localizer.compose_prompt(user_input, messages_history)
        return prompt

    async def finish_get_reply(
        self,
        person: Person,
        context: Context,
        response_message: str,
    ) -> None:
        user_usage = await self._get_user_usage(response_message)
        await self.db.users.add_usage_points(person, user_usage)
        localized_response = await self._get_bot_output(response_message)
        await self.db.dialogs.add_message_to_dialog(
            context,
            "bot",
            localized_response,
            datetime.now(),
        )

    async def get_reply(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> Optional[CommandResponse]:
        prompt = await self.prepare_get_reply(person, context, message)
        if not prompt:
            return None
        response_message = await self.ai.get_reply(prompt)
        await self.finish_get_reply(person, context, response_message)
        return CommandResponse(
            text="message_response", kwargs={"response_text": response_message}
        )

    async def stream_get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        prompt = await self.prepare_get_reply(person, context, message)
        if not prompt:
            return
        response_message = ""
        async for response_message_chunk in self.ai.get_streaming_reply(prompt):
            if not response_message_chunk:
                continue
            response_message += response_message_chunk
            yield CommandResponse(
                text="streaming_message_response",
                kwargs={"response_text": response_message},
            )
        await self.finish_get_reply(person, context, response_message)
