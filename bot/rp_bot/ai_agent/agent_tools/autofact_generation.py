from typing import List
from pydantic import BaseModel, Field
from .base_tool import BaseTool


class UserFact(BaseModel):
    user_fact: str = Field(description="a fact about the user")
    user_handle: str = Field(description="the user handle")


class ChatFacts(BaseModel):
    user_facts: List[UserFact] = Field(description="list of facts about the user")


class CheckIfFactsNeededTool(BaseTool):
    async def run(self) -> bool:
        prompt = "Check if the user prompt requires any facts to be generated."
        result = await self.models_toolkit.text_model.async_ask_yes_no_question(prompt)
        return result


class ComposeFactsBasedOnMessagesTool(BaseTool):
    async def run(self) -> ChatFacts:
        prompt = "Generate a list of facts based on the messages in the chat."
        results: ChatFacts = await self.models_toolkit.text_model.run(
            user_input=prompt,
            pydantic_model=ChatFacts,
        )
        return results
