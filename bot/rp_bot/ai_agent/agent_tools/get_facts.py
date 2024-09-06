from langchain_core.runnables import chain

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context


@chain
async def get_chat_facts(prompt_manager: PromptManager, context: Context) -> str:
    # TODO: pass the user handles
    return prompt_manager.compose_chat_facts_prompt(context)
