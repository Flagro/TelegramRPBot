from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_models import BaseModel
from ...models.handlers_input import Person, Context


class UserIntroductions(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.user_introductions = db.user_introductions

    async def add_introduction(
        self, context: Context, person: Person, introduction: str
    ) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        await self.user_introductions.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {"$set": {"introduction": introduction}},
            upsert=True,
        )

    async def get_user_introduction(self, context: Context, person: Person) -> str:
        chat_id = context.chat_id
        user_handle = person.user_handle
        introduction = await self.user_introductions.find_one(
            {"chat_id": chat_id, "user_handle": user_handle}
        )
        return introduction.get("introduction", "")
