from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_models import BaseModel
from ...models.handlers_input import Person, Context


class UserFacts(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.user_facts = db.user_facts

    async def get_chat_facts(self, context: Context) -> List[str, str]:
        """
        Return a list of facts for the current chat as a list
        user_handle, fact
        """
        chat_id = context.chat_id
        cursor = self.user_facts.find({"chat_id": chat_id})
        facts = []
        async for doc in cursor:
            for fact in doc["facts"]:
                facts.append((doc["user_handle"], fact))
        return facts

    async def get_user_facts(self, context: Context, person: Person) -> List[str]:
        chat_id = context.chat_id
        user_handle = person.user_handle
        facts = await self.user_facts.find_one(
            {"chat_id": chat_id, "user_handle": user_handle}
        )
        return facts.get("facts", [])

    async def add_fact(self, context: Context, person: Person, fact: str) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        await self.user_facts.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {"$push": {"facts": fact}},
            upsert=True,
        )

    async def clear_facts(self, context: Context, facts_user_handle: str) -> None:
        """Delete all facts associated with a user

        Args:
            context (Context): context of the chat
            facts_user_handle (str): user handle to delete facts for
        """
        chat_id = context.chat_id
        await self.user_facts.delete_one(
            {"chat_id": chat_id, "user_handle": facts_user_handle}
        )
