import tiktoken
import io
from typing import AsyncIterator
from openai import OpenAI
from omnimodkit import ModelsToolkit

from ...models.config.ai_config import AIConfig
from ...models.handlers_input import Message, Person, Context
from ...models.base_moderation import ModerationError
from ..prompt_manager import PromptManager
from .agent_tools.agent_toolkit import AIAgentToolkit


class AI:
    def __init__(
        self, openai_api_key: str, ai_config: AIConfig, prompt_manager: PromptManager
    ):
        self.ai_config = ai_config
        self.prompt_manager = prompt_manager
        self.models_toolkit = ModelsToolkit(openai_api_key, ai_config)

    async def engage_is_needed(
        self, person: Person, context: Context, message: Message
    ) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(
            message.message_text
        )
        toolkit = AIAgentToolkit(
            person, context, message, self.models_toolkit, self.prompt_manager
        )
        return await toolkit.check_engage_needed.arun(prompt)

    async def describe_image(
        self,
        person: Person,
        context: Context,
        message: Message,
        in_memory_image_stream: io.BytesIO,
    ) -> str:
        image_information = self.models_toolkit.vision_model.run(in_memory_image_stream)
        image_description = await self.prompt_manager.compose_image_description_prompt(
            image_information
        )
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
        audio_description = await self.prompt_manager.compose_audio_description_prompt(
            audio_information
        )
        return audio_description

    async def generate_image(
        self, person: Person, context: Context, message: Message, prompt: str
    ) -> str:
        """
        Returns the URL of the generated image
        """
        toolkit = AIAgentToolkit(
            person, context, message, self.models_toolkit, self.prompt_manager
        )
        return await toolkit.image_generator.arun(prompt)

    @staticmethod
    def count_tokens(text: str) -> int:
        return tiktoken.count(text)

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.models_toolkit.compose_messages_openai(
            user_input, system_prompt
        )
        return await self.models_toolkit.get_response(messages)

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.models_toolkit.compose_messages_openai(
            user_input, system_prompt
        )
        async for response in self.models_toolkit.get_streaming_response(messages):
            yield response
