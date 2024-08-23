from typing import Optional, AsyncIterator, List
from datetime import datetime

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message, TranscribedMessage
from ..auth import AllowedUser, BotAdmin, NotBanned
from ..rp_bot_handlers import RPBotMessageHandler


class MessageHandler(RPBotMessageHandler):
    permission_classes = (AllowedUser, BotAdmin, NotBanned)

    async def _estimate_reply_usage(
        self, context: Context, transcribed_message: TranscribedMessage
    ) -> int:
        # Estimate the response based on amount of facts in the group chat,
        # the length of the message and wether or not it needs an image generation
        return len(transcribed_message.message_text) // 10 + 1000 * (
            "image" in transcribed_message.message_text
        )

    async def _get_user_usage(self, generated_message: str) -> int:
        return len(generated_message) // 10

    async def _get_transcribed_message(self, message: Message) -> TranscribedMessage:
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
        return TranscribedMessage(
            message_text=message.message_text,
            timestamp=message.timestamp,
            image_description=image_description,
            voice_description=voice_description,
        )

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
        user_transcribed_message = await self._get_transcribed_message(message)
        estimated_usage = await self._estimate_reply_usage(
            context, user_transcribed_message
        )
        user_usage = await self.db.user_usage.get_user_usage(person)
        user_limit = await self.db.user_usage.get_user_usage_limit(person)
        if user_usage + estimated_usage > user_limit:
            self.logger.info(
                f"User {person.user_handle} exceeded the usage limit of {user_limit}"
            )
            # TODO: somehow return a special response from here
            return None
        await self.db.dialogs.add_message_to_dialog(
            context=context,
            person=person,
            transcribed_message=user_transcribed_message,
        )
        if not context.is_bot_mentioned:
            return None
        prompt = await self.prompt_manager.compose_prompt(
            user_transcribed_message, context
        )
        return prompt

    async def finish_get_reply(
        self,
        person: Person,
        context: Context,
        response_message: str,
    ) -> None:
        user_usage = await self._get_user_usage(response_message)
        await self.db.user_usage.add_usage_points(person, user_usage)
        await self.db.dialogs.add_message_to_dialog(
            context,
            "bot",
            TranscribedMessage(
                message_text=response_message,
                timestamp=datetime.now(),
            ),
        )

    async def get_response(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> Optional[CommandResponse]:
        prompt = await self.prepare_get_reply(person, context, message)
        if not prompt:
            return None
        system_prompt = self.prompt_manager.get_reply_system_prompt(context)
        response_message = await self.ai.get_reply(prompt, system_prompt)
        result = CommandResponse(
            text="message_response", kwargs={"response_text": response_message}
        )
        await self.finish_get_reply(person, context, response_message)
        return result

    async def stream_get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        prompt = await self.prepare_get_reply(person, context, message)
        if not prompt:
            return
        response_message = ""
        system_prompt = self.prompt_manager.get_reply_system_prompt(context)
        async for response_message_chunk in self.ai.get_streaming_reply(
            prompt, system_prompt
        ):
            if not response_message_chunk:
                continue
            response_message += response_message_chunk
            yield CommandResponse(
                text="streaming_message_response",
                kwargs={"response_text": response_message},
            )
        await self.finish_get_reply(person, context, response_message)
