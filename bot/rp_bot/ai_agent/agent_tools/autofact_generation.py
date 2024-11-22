from typing import List
from langchain_core.runnables import chain
from langchain_openai import OpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context
from .base_tool import BaseTool


class UserFact(BaseModel):
    user_fact: str = Field(description="a fact about the user")
    user_handle: str = Field(description="the user handle")


class ChatFacts(BaseModel):
    user_facts: List[UserFact] = Field(description="list of facts about the user")


class CheckIfFactsNeededTool(BaseTool):
    async def run(self) -> bool:
        prompt = "Check if the user prompt requires any facts to be generated."
        facts_needed = await self.llm.ainvoke(prompt)
        # TODO: finish this implementation
        return False


class ComposeFactsBasedOnMessagesTool(BaseTool):
    async def run(self) -> ChatFacts:
        prompt = "Generate a list of facts based on the messages in the chat."
        # TODO: generate a chat facts list here
        return []
