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
        return await self.models_toolkit.text_model.ask_yes_no_question(prompt)

    async def describe_image(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_image_stream: io.BytesIO,
    ) -> str:
        image_information = await self.models_toolkit.vision_model.arun(
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
        audio_information = await self.models_toolkit.audio_recognition_model.arun(
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
        async for response in self.models_toolkit.text_model.astream(
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
        # Estimate the response based on amount of facts in the group chat,
        # the length of the message and wether or not it needs an image generation
        # TODO: add proper check for audio length
        audio_length = 100  # estimate for 100 seconds of audio

        # TODO: add proper check for image size
        image_pixels_count = 2048 * 2048  # 2048x2048 image

        token_len = self.ai.count_tokens(message.message_text)

        # TODO: add proper check for image generation need
        image_generation_needed = False

        total_price = self.models_toolkit.get_price(
            token_len=token_len,
            audio_length=audio_length,
            image_pixels_count=image_pixels_count,
            image_generation_needed=image_generation_needed,
        )
        return total_price
