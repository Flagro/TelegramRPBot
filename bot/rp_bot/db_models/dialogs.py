from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Tuple
from datetime import datetime
from .base_models import BaseModel
from ...models.handlers_input import Person, Context


class Dialogs(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.dialogs = db.dialogs

    async def reset(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.dialogs.delete_many({"chat_id": chat_id})

    async def get_messages(
        self, context: Context, last_n: int = 10
    ) -> List[Tuple[str, str]]:
        chat_id = context.chat_id
        cursor = self.dialogs.find(
            {"chat_id": chat_id},
            {"_id": 0, "messages": {"$slice": -last_n}},
        )
        messages = []
        async for doc in cursor:
            messages.extend(doc.get("messages", []))
        return messages

    async def add_user_message_to_dialog(
        self, context: Context, person: Person, message: str, timestamp: datetime
    ) -> None:
        user_handle = person.user_handle
        await self.dialogs.update_one(
            {"chat_id": context.chat_id, "user_handle": user_handle},
            {"$push": {"messages": message}},
            upsert=True,
        )

    async def add_bot_response_to_dialog(
        self, context: Context, message: str, timestamp: datetime
    ) -> None:
        chat_id = context.chat_id
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": "bot"},
            {"$push": {"messages": message}},
            upsert=True,
        )
