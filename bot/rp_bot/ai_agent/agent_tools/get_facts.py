from langchain_core.runnables import chain

from ...db import DB
from ...prompt_manager import PromptManager
from ....models.handlers_input import Context
from .base_tool import BaseTool


class GetUserFactsTool(BaseTool):
    async def run(self, context: Context, user_handle: str) -> str:
        person = await self.db.users.get_person_by_handle(user_handle)
        return self.prompt_manager.compose_user_facts_prompt(person, context)


class GetChatFactsTool(BaseTool):
    async def run(self, context: Context) -> str:
        return self.prompt_manager.compose_chat_facts_prompt(context)
