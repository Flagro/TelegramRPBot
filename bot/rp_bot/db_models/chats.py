from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from .base_models import BaseModel
from ...models.handlers_input import Person, Context


class Chats(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase, default_language: str) -> None:
        super().__init__(db)
        self.chats = db.chats
        self.default_language = default_language

    async def create_chat_if_not_exists(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.chats.update_one(
            {"chat_id": chat_id},
            {
                "$setOnInsert": {
                    "chat_id": chat_id,
                    "language": self.default_language,
                    "is_started": False,
                    "conversation_tracker": False,
                }
            },
            upsert=True,
        )

    async def start_chat(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"is_started": True}},
        )

    async def chat_is_started(self, context: Context) -> bool:
        """Check if chat is started
        by checking the flag is_started in the chat document
        """
        chat_id = context.chat_id
        chat_data = await self.chats.find_one(
            {"chat_id": chat_id}, {"_id": 0, "is_started": 1}
        )
        return chat_data.get("is_started", False)

    async def stop_chat(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"is_started": False}},
        )

    async def set_language(self, context: Context, language: str) -> None:
        chat_id = context.chat_id
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"language": language}},
        )

    async def get_language(self, context: Context) -> Optional[str]:
        chat_id = context.chat_id
        chat_data = await self.chats.find_one(
            {"chat_id": chat_id}, {"_id": 0, "language": 1}
        )
        return chat_data.get("language")

    async def get_conversation_tracker_state(self, context: Context) -> bool:
        chat_id = context.chat_id
        chat_data = await self.chats.find_one(
            {"chat_id": chat_id}, {"_id": 0, "conversation_tracker": 1}
        )
        return chat_data.get("conversation_tracker", False)

    async def switch_conversation_tracker(self, context: Context) -> bool:
        old_conversation_tracker_state = await self.get_conversation_tracker_state(
            context
        )
        new_conversation_tracker_state = not old_conversation_tracker_state
        await self.chat_modes.update_one(
            {"chat_id": context.chat_id},
            {"$set": {"conversation_tracker": new_conversation_tracker_state}},
        )
        return new_conversation_tracker_state
