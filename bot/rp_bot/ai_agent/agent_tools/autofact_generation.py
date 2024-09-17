from typing import List
from langchain_core.runnables import chain
from langchain_openai import OpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context


class UserFact(BaseModel):
    user_fact: str = Field(description="a fact about the user")
    user_handle: str = Field(description="the user handle")


class ChatFacts(BaseModel):
    user_facts: List[UserFact] = Field(description="list of facts about the user")


@chain
async def check_if_facts_needed(
    prompt_manager: PromptManager, context: Context, llm: OpenAI
) -> bool:
    prompt = prompt_manager.compose_check_if_facts_needed_prompt(context)
    facts_needed = await llm.ainvoke(prompt)
    # TODO: finish this implementation
    return False


@chain
async def compsoe_facts_based_on_messages(
    db: DB, prompt_manager: PromptManager, context: Context
) -> ChatFacts:
    prompt = prompt_manager.compose_facts_based_on_messages_prompt(context)
    # TODO: generate a chat facts list here
    return []
