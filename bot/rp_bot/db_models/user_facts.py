from typing import List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_db_model import BaseDBModel
from ...models.handlers_input import Person, Context


class UserFacts(BaseDBModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.user_facts = db.user_facts

    async def get_chat_facts(self, context: Context) -> List[Tuple[str, str]]:
        """
        Return a list of facts for the current chat as a list
        user_handle, fact
        """
        cursor = self.user_facts.find({"chat_id": context.chat_id})
        facts = []
        async for doc in cursor:
            for fact in doc["facts"]:
                facts.append((doc["user_handle"], fact))
        return facts

    async def get_user_facts(self, context: Context, person: Person) -> List[str]:
        facts = await self.user_facts.find_one(
            {"chat_id": context.chat_id, "user_handle": person.user_handle}
        )
        return facts.get("facts", []) if facts else []

    async def get_facts_for_user_handle(
        self, context: Context, user_handle: str
    ) -> List[str]:
        """Get all facts for a user handle in the current chat

        Args:
            context (Context): context of the chat
            user_handle (str): user handle to get facts for

        Returns:
            List[str]: list of facts
        """
        facts = await self.user_facts.find_one(
            {"chat_id": context.chat_id, "user_handle": user_handle}
        )
        return facts.get("facts", []) if facts else []

    async def add_fact(
        self, context: Context, facts_user_handle: str, fact: str
    ) -> None:
        await self.user_facts.update_one(
            {"chat_id": context.chat_id, "user_handle": facts_user_handle},
            {"$push": {"facts": fact}},
            upsert=True,
        )

    async def clear_facts(self, context: Context, facts_user_handle: str) -> None:
        """Delete all facts associated with a user

        Args:
            context (Context): context of the chat
            facts_user_handle (str): user handle to delete facts for
        """
        await self.user_facts.delete_one(
            {"chat_id": context.chat_id, "user_handle": facts_user_handle}
        )
