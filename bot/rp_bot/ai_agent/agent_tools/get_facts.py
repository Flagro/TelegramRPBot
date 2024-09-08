from langchain_core.runnables import chain

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context


@chain
async def get_chat_facts(prompt_manager: PromptManager, context: Context) -> str:
    return prompt_manager.compose_chat_facts_prompt(context)


@chain
async def get_user_facts(
    db: DB, prompt_manager: PromptManager, context: Context, user_handle: str
) -> str:
    person = db.users.get_person_by_handle(user_handle)
    return prompt_manager.compose_user_facts_prompt(person, context)
