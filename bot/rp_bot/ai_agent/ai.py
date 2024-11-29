import tiktoken
import io
from typing import AsyncIterator, List, Dict, Any
from openai import OpenAI

from ...models.config.ai_config import AIConfig
from ...models.handlers_input import Message, Person, Context
from ...models.base_moderation import ModerationError
from ..prompt_manager import PromptManager
from .ai_utils.describe_image import describe_image
from .models_toolkit import ModelsToolkit
from .moderation import Moderation
from .agent_tools.agent_toolkit import AIAgentToolkit


class AI:
    def __init__(
        self, openai_api_key: str, ai_config: AIConfig, prompt_manager: PromptManager
    ):
        moderation_model = OpenAI(api_key=openai_api_key)
        self.moderation = Moderation(model=moderation_model)
        self.ai_config = ai_config
        self.prompt_manager = prompt_manager
        self.models_toolkit = ModelsToolkit(openai_api_key, ai_config)

    async def engage_is_needed(
        self, person: Person, context: Context, message: Message
    ) -> bool:
        prompt = await self.prompt_manager.compose_engage_needed_prompt(
            message.message_text
        )
        toolkit = AIAgentToolkit(person, context, message, self.models_toolkit)
        return await toolkit.check_engage_needed.run(prompt)

    async def describe_image(self, in_memory_image_stream: io.BytesIO) -> str:
        if not self.moderation.moderate_image(in_memory_image_stream):
            raise ModerationError("Image is not safe")
        # TODO: pass the image model into the chain
        image_information = await describe_image(in_memory_image_stream)
        image_description = await self.prompt_manager.compose_image_description_prompt(
            image_information
        )
        return image_description

    async def transcribe_audio(self, in_memory_audio_stream: io.BytesIO) -> str:
        if not self.moderation.moderate_audio(in_memory_audio_stream):
            raise ModerationError("Audio is not safe")
        # TODO: implement this
        # r = await openai.Audio.atranscribe(in_memory_audio_stream)
        # return r["text"] or ""
        return ""

    async def generate_image(
        self, person: Person, context: Context, message: Message, prompt: str
    ) -> str:
        """
        Returns the URL of the generated image
        """
        toolkit = AIAgentToolkit(person, context, message, self.models_toolkit)
        return await toolkit.image_generator.run(prompt)

    @staticmethod
    def count_tokens(text: str) -> int:
        return tiktoken.count(text)

    @staticmethod
    def compose_messages_openai(user_input: str, system_prompt: str) -> list:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

    def create_response(
        self, messages: List[Dict[str, str]], stream: bool = False
    ) -> Any:
        # TODO: Fix Any return type
        return self.llm.chat.completions.create(
            model=self._get_default_model("text").name,
            messages=messages,
            stream=stream,
            temperature=self.ai_config.TextGeneration.temperature,
        )

    async def get_reply(self, user_input: str, system_prompt: str) -> str:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.compose_messages_openai(user_input, system_prompt)
        response = self.create_response(messages)
        return response.choices[0].message.content

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        if not self.moderation.moderate_text(user_input):
            raise ModerationError("Text is not safe")
        messages = self.compose_messages_openai(user_input, system_prompt)
        response = self.create_response(messages, stream=True)
        for chunk in response:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
