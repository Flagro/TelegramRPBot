import io
from logging import Logger
from typing import AsyncIterator, Optional
from pydantic import BaseModel, Field, ConfigDict
from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from .agent_toolkit import AIAgentToolkit
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message, TranscribedMessage


class AIAgentStreamingResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    text_chunk: str = Field(default="")
    total_text: str = Field(default="")
    image_url: Optional[str] = Field(default=None)
    audio_bytes: Optional[io.BytesIO] = Field(default=None)
    price: float = Field(default=0.0)

    transcribed_user_message: TranscribedMessage = Field(default=None)


class AIAgent:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        db: AsyncIOMotorDatabase,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
        logger: Logger,
    ):
        self.person = person
        self.context = context
        self.message = message
        self.db = db
        self.models_toolkit = models_toolkit
        self.prompt_manager = prompt_manager
        self.toolkit = AIAgentToolkit(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.models_toolkit = models_toolkit
        self.logger = logger

    async def _get_transcribed_message(self) -> TranscribedMessage:
        # Note that here the responsibility to pass NULL images and Audio is on the
        # outer level bot processing (TG bot or other bot)
        image_description = (
            str(
                await self.models_toolkit.vision_model.arun_default(
                    in_memory_image_stream=self.message.in_file_image
                )
            )
            if self.message.in_file_image
            else None
        )
        voice_description = (
            str(
                await self.models_toolkit.audio_recognition_model.arun_default(
                    in_memory_audio_stream=self.message.in_file_audio
                )
            )
            if self.message.in_file_audio
            else None
        )
        return TranscribedMessage(
            message_text=self.message.message_text,
            timestamp=self.message.timestamp,
            image_description=image_description,
            voice_description=voice_description,
        )

    async def astream(
        self,
    ) -> AsyncIterator[AIAgentStreamingResponse]:
        transcribed_user_message = await self._get_transcribed_message()
        prompt = await self.prompt_manager.compose_prompt(
            initiator=self.person,
            context=self.context,
            user_transcribed_message=transcribed_user_message,
        )
        system_prompt = await self.prompt_manager.get_reply_system_prompt(
            context=self.context
        )
        total_text = ""
        async for response in self.models_toolkit.text_model.astream_default(
            user_input=prompt, system_prompt=system_prompt
        ):
            total_text += response.text_chunk
            if response is not None:
                yield AIAgentStreamingResponse(
                    text_chunk=response.text_chunk,
                    total_text=total_text,
                    image_url=None,
                    audio_bytes=None,
                    price=0.0,
                    transcribed_user_message=transcribed_user_message,
                )
