import io
from typing import AsyncIterator
from omnimodkit import ModelsToolkit
from omnimodkit.ai_config import AIConfig
from motor.motor_asyncio import AsyncIOMotorDatabase

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
        return await self.models_toolkit.text_model.async_ask_yes_no_question(prompt)

    async def describe_image(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_image_stream: io.BytesIO,
    ) -> str:
        image_information = await self.models_toolkit.vision_model.arun_default(
            in_memory_image_stream
        )
        image_description = str(image_information)
        return image_description

    async def transcribe_audio(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_audio_stream: io.BytesIO,
    ) -> str:
        audio_information = (
            await self.models_toolkit.audio_recognition_model.arun_default(
                in_memory_audio_stream
            )
        )
        audio_description = str(audio_information)
        return audio_description

    async def generate_image(
        self, person: Person, context: Context, message: Message, prompt: str
    ) -> str:
        """
        Returns the URL of the generated image
        """
        return await self.models_toolkit.image_generation_model.arun_default(prompt)

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        return await self.models_toolkit.text_model.arun_default(
            user_input, system_prompt
        )

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        async for response in self.models_toolkit.text_model.astream_default(
            user_input, system_prompt
        ):
            yield response

    async def get_price(
        self,
        message: Message,
    ) -> float:
        """
        Returns the price of the message
        """
        # TODO: take into account the output as well
        return self.models_toolkit.get_price(
            input_text=message.message_text,
            input_image=message.in_file_image,
            input_audio=message.in_file_audio,
        )

    async def estimate_price(self, message: Message) -> float:
        """
        Estimates the price of the message
        """
        return self.models_toolkit.estimate_price(
            input_text=message.message_text,
            input_image=message.in_file_image,
            input_audio=message.in_file_audio,
        )

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a text string.
        """
        return self.models_toolkit.text_model.count_tokens(text)
