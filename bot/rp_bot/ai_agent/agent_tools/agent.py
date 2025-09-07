import io
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


class AIAgent:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        db: AsyncIOMotorDatabase,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
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

    async def astream(
        self,
    ) -> AsyncIterator[AIAgentStreamingResponse]:
        prompt = await self.prompt_manager.get_prompt_from_transcribed_message(
            person=self.person,
            context=self.context,
            transcribed_message=TranscribedMessage(
                message_text=self.message.message_text,
                timestamp=self.message.timestamp,
            ),
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
                )
