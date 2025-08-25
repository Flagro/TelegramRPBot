from typing import AsyncIterator
from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from .agent_toolkit import AIAgentToolkit
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message


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
        self.toolkit = AIAgentToolkit(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.models_toolkit = models_toolkit

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        response = await self.models_toolkit.text_model.arun_default(
            user_input, system_prompt
        )
        return response.text

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        async for response in self.models_toolkit.text_model.astream_default(
            user_input, system_prompt
        ):
            if response is not None:
                yield response.text_chunk
