from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_models import BaseModel
from ...models.handlers_input import Person, Context


class UserFacts(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.user_facts = db.user_facts

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
