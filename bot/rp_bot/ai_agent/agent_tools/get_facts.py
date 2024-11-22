from .base_tool import BaseTool


class GetUserFactsTool(BaseTool):
    async def run(self, user_handle: str) -> str:
        person = await self.db.users.get_person_by_handle(user_handle)
        return self.prompt_manager.compose_user_facts_prompt(person, self.context)


class GetChatFactsTool(BaseTool):
    async def run(self) -> str:
        return self.prompt_manager.compose_chat_facts_prompt(self.context)
