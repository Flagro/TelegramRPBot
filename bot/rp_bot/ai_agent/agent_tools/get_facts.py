from langchain_core.runnables import chain

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context


@chain
async def get_chat_facts(prompt_manager: PromptManager, context: Context) -> str:
    # TODO: pass the user handles
    return prompt_manager.compose_chat_facts_prompt(context)


@chain
async def get_user_facts(
    db: DB, prompt_manager: PromptManager, context: Context, user_handle: str
) -> str:
    # TODO: pass the user handles
    # TODO: get the proper Person from the db
    return prompt_manager.compose_user_facts_prompt(
        Person(user_handle=user_handle), context
    )
