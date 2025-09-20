from typing import List, Optional
from pydantic import BaseModel, Field
from omnimodkit.base_toolkit_model import OpenAIMessage
from .base_tool import BaseTool
from .agent import AIAgentStreamingResponse
from ....models.handlers_input import TranscribedMessage


class UserFact(BaseModel):
    user_fact: str = Field(description="a fact about the user")
    user_handle: str = Field(description="the user handle")


class ChatFacts(BaseModel):
    user_facts: List[UserFact] = Field(description="list of facts about the user")


class CheckIfFactsNeededTool(BaseTool):
    async def run(
        self,
        output: AIAgentStreamingResponse,
        transcribed_user_message: TranscribedMessage,
        system_prompt: Optional[str] = None,
        communication_history: Optional[List[OpenAIMessage]] = None,
    ) -> bool:
        """
        Check if the user prompt requires any facts to be generated.
        """
        prompt = (
            "Check if the user prompt requires any facts to be generated."
            f"{output.total_text}\n\n"
            f"{transcribed_user_message.message_text}\n\n"
            f"{system_prompt}\n\n"
            f"{communication_history}\n\n"
        )
        result = await self.models_toolkit.text_model.async_ask_yes_no_question(prompt)
        return result


class ComposeFactsBasedOnMessagesTool(BaseTool):
    async def run(
        self,
        output: AIAgentStreamingResponse,
        transcribed_user_message: TranscribedMessage,
        system_prompt: Optional[str] = None,
        communication_history: Optional[List[OpenAIMessage]] = None,
    ) -> ChatFacts:
        prompt = (
            "Generate a list of facts based on the latest message from the user in the chat."
            f"{output.total_text}\n\n"
            f"{transcribed_user_message.message_text}\n\n"
            f"{system_prompt}\n\n"
            f"{communication_history}\n\n"
        )
        results: ChatFacts = await self.models_toolkit.text_model.run(
            user_input=prompt,
            pydantic_model=ChatFacts,
        )
        return results
