import io
from typing import AsyncIterator
from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...models.config.ai_config import AIConfig
from ...models.handlers_input import Message, Person, Context
from ..prompt_manager import PromptManager


class AI:
    def __init__(
        self,
        openai_api_key: str,
        ai_config: AIConfig,
        prompt_manager: PromptManager,
        db: AsyncIOMotorDatabase,
    ):
        self.ai_config = ai_config
        self.prompt_manager = prompt_manager
        self.models_toolkit = ModelsToolkit(openai_api_key, ai_config)
        self.db = db

    async def engage_is_needed(
        self, person: Person, context: Context, message: Message
    ) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(
            message.message_text
        )
        return self.models_toolkit.text_model.ask_yes_no_question(prompt)

    async def describe_image(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_image_stream: io.BytesIO,
    ) -> str:
        image_information = self.models_toolkit.vision_model.run(in_memory_image_stream)
        image_description = str(image_information)
        return image_description

    async def transcribe_audio(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_audio_stream: io.BytesIO,
    ) -> str:
        audio_information = self.models_toolkit.audio_recognition_model.run(
            in_memory_audio_stream
        )
        audio_description = str(audio_information)
        return audio_description

    async def generate_image(
        self, person: Person, context: Context, message: Message, prompt: str
    ) -> str:
        """
        Returns the URL of the generated image
        """
        return await self.models_toolkit.image_generation_model.arun(prompt)

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        return await self.models_toolkit.text_model(user_input, system_prompt)

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        async for response in self.models_toolkit.text_model.stream(
            user_input, system_prompt
        ):
            yield response
