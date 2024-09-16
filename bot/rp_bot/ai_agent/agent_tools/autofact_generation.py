from langchain_core.runnables import chain
from langchain_openai import OpenAI

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context


@chain
async def check_if_facts_needed(prompt_manager: PromptManager, context: Context, llm: OpenAI) -> bool:
    prompt = prompt_manager.compose_check_if_facts_needed_prompt(context)
    facts_needed = await llm.invoke(prompt)
    # TODO: finish this implementation
    return False
