from langchain_core.runnables import chain

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context
from .base_tool import BaseTool


@chain
async def get_chat_facts(prompt_manager: PromptManager, context: Context) -> str:
    return prompt_manager.compose_chat_facts_prompt(context)


@chain
async def get_user_facts(
    db: DB, prompt_manager: PromptManager, context: Context, user_handle: str
) -> str:
    person = await db.users.get_person_by_handle(user_handle)
    return prompt_manager.compose_user_facts_prompt(person, context)


class GetUserFactsTool(BaseTool):
    async def run(self, context: Context, user_handle: str) -> str:
        return await get_user_facts(context=context, user_handle=user_handle)


class GetChatFactsTool(BaseTool):
    async def run(self, context: Context) -> str:
        return await get_chat_facts(context=context)
