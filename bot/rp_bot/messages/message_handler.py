from typing import Optional, AsyncIterator, List
from datetime import datetime

from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message, TranscribedMessage
from ..auth import AllowedUser, BotAdmin, NotBanned
from ..rp_bot_handlers import RPBotMessageHandler
from ..ai_agent.agent_tools.agent import AIAgent


class MessageHandler(RPBotMessageHandler):
    permission_classes = (AllowedUser, BotAdmin, NotBanned)

    async def estimate_price(self, message: Message) -> float:
        """
        Estimates the price of the message
        """
        return self.models_toolkit.estimate_price(
            input_text=message.message_text,
            input_image=message.in_file_image,
            input_audio=message.in_file_audio,
        )

    async def _get_transcribed_message(self, message: Message) -> TranscribedMessage:
        # Note that here the responsibility to pass NULL images and Audio is on the
        # outer level bot processing (TG bot or other bot)
        image_description = (
            str(
                await self.models_toolkit.vision_model.arun_default(
                    in_memory_image_stream=message.in_file_image
                )
            )
            if message.in_file_image
            else None
        )
        voice_description = (
            str(
                await self.models_toolkit.audio_recognition_model.arun_default(
                    in_memory_audio_stream=message.in_file_audio
                )
            )
            if message.in_file_audio
            else None
        )
        return TranscribedMessage(
            message_text=message.message_text,
            timestamp=message.timestamp,
            image_description=image_description,
            voice_description=voice_description,
        )

    async def is_usage_under_limit(
        self, person: Person, context: Context, transcribed_message: TranscribedMessage
    ) -> bool:
        estimated_usage = await self.estimate_price(message=transcribed_message)
        user_usage = await self.db.user_usage.get_user_usage(person=person)
        user_limit = await self.db.user_usage.get_user_usage_limit(person=person)
        return user_usage + estimated_usage < user_limit

    async def get_usage_over_limit_response(self, person: Person) -> CommandResponse:
        usage_limit = await self.db.user_usage.get_user_usage_limit(person=person)
        return CommandResponse(
            text="usage_limit_exceeded",
            kwargs={"user_handle": person.user_handle, "usage_limit": usage_limit},
        )

    async def get_prompt_from_transcribed_message(
        self, person: Person, context: Context, transcribed_message: TranscribedMessage
    ) -> str:
        prompt = await self.prompt_manager.compose_prompt(
            initiator=person,
            context=context,
            user_transcribed_message=transcribed_message,
        )
        self.logger.info(
            "Using AI to generate a response to the message from "
            f"{person.user_handle} in chat {context.chat_id}"
        )
        return prompt

    async def get_response(
        self,
        person: Person,
        context: Context,
        message: Message,
        args: List[str],
    ) -> Optional[CommandResponse]:
        last_command_response = None
        async for command_response in self.stream_get_response(
            person=person, context=context, message=message, args=args
        ):
            if not command_response:
                continue
            last_command_response = command_response
        return last_command_response

    async def stream_get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        # Prepare and analyze the message (formerly prepare_get_reply logic)
        conversation_tracker_enabled = (
            await self.db.chats.get_conversation_tracker_state(context=context)
        )
        chat_is_started = await self.db.chats.chat_is_started(context=context)
        if not chat_is_started or (
            not conversation_tracker_enabled and not context.is_bot_mentioned
        ):
            self.logger.info(
                f"Ignoring message from {person.user_handle} in chat {context.chat_id}"
            )
            return

        autoengage_state = await self.db.chats.get_autoengage_state(context=context)
        engage_is_needed = False
        if autoengage_state:
            prompt = await self.prompt_manager.compose_engage_needed_prompt(
                user_input=message.message_text
            )
            engage_is_needed = (
                await self.models_toolkit.text_model.async_ask_yes_no_question(
                    question=prompt
                )
            )

        # Determine if we should engage or just save to DB
        should_engage = engage_is_needed or context.is_bot_mentioned
        save_message_to_db = True

        if save_message_to_db and not should_engage:
            # Save message without transcribing to save resources
            await self.db.dialogs.add_message_to_dialog(
                context=context,
                person=person,
                transcribed_message=TranscribedMessage(
                    message_text=message.message_text,
                    timestamp=message.timestamp,
                ),
            )
            self.logger.info(
                f"Saving the message from {person.user_handle} in chat {context.chat_id} "
                "as context for future responses and not generating a response"
            )
            return

        if not should_engage:
            return

        if not context.is_bot_mentioned and engage_is_needed:
            self.logger.info(
                f"Engaging with the message from {person.user_handle} in chat {context.chat_id} "
                "as the agent detected a question or a request for information"
            )

        if not await self.is_usage_under_limit(
            person=person, context=context, transcribed_message=message
        ):
            yield await self.get_usage_over_limit_response(person=person)
            return

        ai_agent = AIAgent(
            person=person,
            context=context,
            message=message,
            db=self.db,
            models_toolkit=self.models_toolkit,
            prompt_manager=self.prompt_manager,
        )
        agent_response = None
        async for agent_response in ai_agent.astream():
            if not agent_response.text_chunk:
                continue
            yield CommandResponse(
                text="streaming_message_response",
                kwargs={"response_text": agent_response.total_text},
            )

        await self.db.dialogs.add_message_to_dialog(
            context=context,
            person=person,
            transcribed_message=TranscribedMessage(
                message_text=message.message_text,
                timestamp=message.timestamp,
            ),
        )
        if agent_response:
            await self.db.user_usage.add_usage_points(
                person=person, points=agent_response.price
            )
            await self.db.dialogs.add_message_to_dialog(
                context=context,
                person="bot",
                transcribed_message=TranscribedMessage(
                    message_text=agent_response.total_text,
                    timestamp=datetime.now(),
                ),
            )
            self.logger.info(
                f"Generated a response for the message from {person.user_handle} in chat {context.chat_id} "
                f"with usage of {agent_response.price}"
            )
        else:
            self.logger.info(
                f"No response generated for the message from {person.user_handle} in chat {context.chat_id}"
            )
