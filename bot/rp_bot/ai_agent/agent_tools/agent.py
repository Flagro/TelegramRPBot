import io
import asyncio
from typing import (
    Optional,
    Union,
    AsyncGenerator,
    List,
    Protocol,
    Type,
    Literal,
)
from logging import Logger
from pydantic import BaseModel, Field, ConfigDict, create_model
from omnimodkit import ModelsToolkit
from omnimodkit.models_toolkit import ModelsToolkit, AvailableModelType
from omnimodkit.base_toolkit_model import OpenAIMessage
from motor.motor_asyncio import AsyncIOMotorDatabase
from .agent_toolkit import AIAgentToolkit
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message, TranscribedMessage
from .autofact_generation import UserFact


class AIAgentResponseOutputTypeModel(Protocol):
    """Protocol for dynamically created models with output_type field."""

    output_type: Union[type, object]


class TextStreamingResponse(BaseModel):
    """
    The most common output type - use it by default.
    By selecting this output type, the text generation will be used.
    """

    text_response: bool = Field(
        default=False,
        description="Indicates if the response is a text response.",
    )


class AudioResponse(BaseModel):
    """
    By selecting this output type, the audio generation will be used.
    Use this output type only when excplitily requested since it is expensive.
    """

    audio_text_to_generate: str = Field(
        default="",
        description="Audio text to generate in the language of the user.",
    )
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = Field(
        default="alloy",
        description=(
            "Use alloy by default. However if user requests something specific, choose according to the following personas:\n"
            "alloy - warm, clear, and versatile; a balanced voice that adapts easily to formal or casual settings.\n"
            "echo - energetic and bright, with an expressive, youthful enthusiasm that makes conversations feel lively.\n"
            "fable - calm, narrative, and a bit whimsical; sounds like a storyteller guiding listeners through ideas.\n"
            "onyx - deep, confident, and steady; conveys authority and composure without being harsh.\n"
            "nova - friendly, approachable, and modern; upbeat and easygoing, like chatting with a helpful companion.\n"
            "shimmer - gentle, melodic, and slightly playful; soothing with a touch of sparkle, making interactions feel engaging and pleasant."
        ),
    )


class TextWithImageStreamingResponse(BaseModel):
    """
    By selecting this output type, the text generation will be used along with image generation.
    Note that the image generation is expensive and should be used only when explicitly requested
    or when it corresponds to the agent's personality.
    """

    text_generation_needed: bool = Field(
        default=False,
        description="Indicates if text generation is needed.",
    )
    image_description_to_generate: str = Field(
        default="",
        description="Description of the generated image in the language of the user.",
    )


class AIAgentStreamingResponse(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    is_final_response: bool = Field(
        default=True,
        description="Indicates if the response is the final response.",
    )
    total_text: Optional[str] = Field(
        default=None,
        description="Text response from the model.",
    )
    text_new_chunk: Optional[str] = Field(
        default=None,
        description="New chunk of text response from the model.",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="Generated image URL response from the model.",
    )
    image_description: Optional[str] = Field(
        default=None,
        description="Description of the generated image.",
    )
    audio_bytes: Optional[io.BytesIO] = Field(
        default=None,
        description="In-memory audio bytes response from the model.",
    )
    audio_description: Optional[str] = Field(
        default=None,
        description="Description of the generated audio.",
    )
    total_price: Optional[float] = Field(
        default=None,
        description="Total price of the model response based on input and output.",
    )
    transcribed_user_message: TranscribedMessage = Field(default=None)
    generated_facts: List[UserFact] = Field(
        default_factory=list, description="Generated facts about the users in the chat."
    )


class AIAgent:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        db: AsyncIOMotorDatabase,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
        autofact_enabled: bool,
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
        self.autofact_enabled = autofact_enabled
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

    def _compose_user_input(
        self,
        user_input: Optional[str] = None,
        image_description: Optional[str] = None,
        audio_description: Optional[str] = None,
    ) -> str:
        prompts = []
        if user_input:
            prompts.append(user_input)
        if image_description:
            prompts.append(image_description)
        if audio_description:
            prompts.append(audio_description)
        return "\n".join(prompts)

    def _can_use_model(self, model_type: AvailableModelType) -> bool:
        """
        Check if a specific model type is allowed.
        """
        return self.models_toolkit.can_use_model(model_type)

    def _get_allowed_output_types(self) -> List[type]:
        """
        Get the list of allowed output type classes based on allowed_models.
        """
        allowed_types = []

        if self._can_use_model("text"):
            allowed_types.append(TextStreamingResponse)

        if self._can_use_model("audio_generation"):
            allowed_types.append(AudioResponse)

        if self._can_use_model("text") and self._can_use_model("image_generation"):
            allowed_types.append(TextWithImageStreamingResponse)

        return allowed_types

    def _create_dynamic_output_type_model(self) -> Type[AIAgentResponseOutputTypeModel]:
        """
        Create a dynamic output type model based on allowed models.
        """
        allowed_types = self._get_allowed_output_types()

        union_types = allowed_types or [TextStreamingResponse]

        if len(union_types) == 1:
            union_type = union_types[0]
        else:
            union_type = Union[tuple(union_types)]

        DynamicAIAgentStreamingResponseType = create_model(
            "DynamicAIAgentStreamingResponseType",
            output_type=(
                union_type,
                Field(description="Type of output expected from the model."),
            ),
        )

        return DynamicAIAgentStreamingResponseType

    async def astream(self) -> AsyncGenerator[AIAgentStreamingResponse, None]:
        """
        Asynchronously run the OmniModel with the provided inputs and return the output.
        """
        transcribed_user_message = await self._get_transcribed_message()
        user_input = await self.prompt_manager.compose_prompt(
            initiator=self.person,
            context=self.context,
            user_transcribed_message=transcribed_user_message,
        )
        system_prompt = await self.prompt_manager.get_reply_system_prompt(
            context=self.context
        )
        # Explicit communication history confuses the structured output generation
        communication_history = None

        # Determine the output type based on the input data
        dynamic_output_type_model = self._create_dynamic_output_type_model()
        output_type_model: AIAgentResponseOutputTypeModel = (
            await self.models_toolkit.text_model.arun(
                system_prompt=system_prompt,
                pydantic_model=dynamic_output_type_model,
                user_input=user_input,
                communication_history=communication_history,
            )
        )
        output_type = output_type_model.output_type

        # Process the input data based on the output type
        if isinstance(output_type, AudioResponse):
            if not self._can_use_model("audio_generation"):
                raise ValueError(
                    "Audio generation is not allowed with the current model configuration."
                )
            audio_response = (
                await self.models_toolkit.audio_generation_model.arun_default(
                    system_prompt=system_prompt,
                    user_input=output_type.audio_text_to_generate,
                    voice=output_type.voice,
                    communication_history=communication_history,
                )
            )
            final_response = AIAgentStreamingResponse(
                audio_bytes=audio_response.audio_bytes,
                audio_description=output_type.audio_text_to_generate,
            )
        elif isinstance(output_type, TextWithImageStreamingResponse):
            if not self._can_use_model("image_generation"):
                raise ValueError(
                    "Image generation is not allowed with the current model configuration."
                )
            image_response_task = asyncio.create_task(
                self.models_toolkit.image_generation_model.arun_default(
                    system_prompt=system_prompt,
                    user_input=output_type.image_description_to_generate,
                    communication_history=communication_history,
                )
            )
            adjusted_text_generation_system_prompt = (
                f"{system_prompt}\n"
                "Generate text assuming that the image with the following description has "
                "already been generated and it will be attached to the response as an attachment "
                "automatically (do not mention it in the text):"
                f"\n{output_type.image_description_to_generate}"
            )
            total_text = ""
            async for chunk in self.models_toolkit.text_model.astream_default(
                system_prompt=adjusted_text_generation_system_prompt,
                user_input=user_input,
                communication_history=communication_history,
            ):
                if chunk.text_chunk:
                    total_text += chunk.text_chunk
                    yield AIAgentStreamingResponse(
                        is_final_response=False,
                        total_text=total_text,
                        text_new_chunk=chunk.text_chunk,
                    )
            image_response = await image_response_task
            final_response = AIAgentStreamingResponse(
                total_text=total_text,
                image_url=image_response.image_url,
                image_description=output_type.image_description_to_generate,
            )
        elif isinstance(output_type, TextStreamingResponse):
            total_text = ""
            async for chunk in self.models_toolkit.text_model.astream_default(
                system_prompt=system_prompt,
                user_input=user_input,
                communication_history=communication_history,
            ):
                total_text += chunk.text_chunk
                yield AIAgentStreamingResponse(
                    is_final_response=False,
                    total_text=total_text,
                    text_new_chunk=chunk.text_chunk,
                )
            final_response = AIAgentStreamingResponse(
                total_text=total_text, text_new_chunk=""
            )
        else:
            raise ValueError("Unexpected output type received from the model.")
        yield self.inject_price(
            output=final_response,
            transcribed_user_message=transcribed_user_message,
            system_prompt=system_prompt,
            communication_history=communication_history,
        )

    def inject_price(
        self,
        output: AIAgentStreamingResponse,
        transcribed_user_message: TranscribedMessage,
        system_prompt: Optional[str] = None,
        communication_history: Optional[List[OpenAIMessage]] = None,
    ) -> AIAgentStreamingResponse:
        """
        Inject the price into the AIAgentStreamingResponse based on the input and output.
        """
        total_input_text = (
            (transcribed_user_message.message_text or "")
            + (system_prompt or "")
            + "\n".join([msg["text"] for msg in communication_history or []])
        )

        # Only calculate prices for allowed models
        input_image = (
            transcribed_user_message.image_description
            if self._can_use_model("vision")
            else None
        )
        output_image_url = (
            output.image_url if self._can_use_model("image_generation") else None
        )
        input_audio = (
            transcribed_user_message.voice_description
            if self._can_use_model("audio_recognition")
            else None
        )
        output_audio = (
            output.audio_bytes if self._can_use_model("audio_generation") else None
        )

        price = self.models_toolkit.get_price(
            input_text=total_input_text,
            output_text=output.total_text,
            input_image=input_image,
            output_image_url=output_image_url,
            input_audio=input_audio,
            output_audio=output_audio,
        )
        modified_response = output
        modified_response.total_price = price
        return modified_response
