from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from uuid import UUID
from collections import namedtuple
from .base_models import BaseModel
from ...models.config import DefaultChatModes
from ...models.handlers_input import Person, Context


ChatModeResponse = namedtuple(
    "ChatModeResponse", ["id", "mode_name", "mode_description"]
)


class Chats(BaseModel):
    def __init__(
        self, db: AsyncIOMotorDatabase, default_chat_modes: DefaultChatModes
    ) -> None:
        super().__init__(db)
        self.chat_modes = db.chat_modes
        self.default_chat_modes = default_chat_modes

    def _init_default_chat_modes(self, context: Context) -> None:
        chat_id = context.chat_id
        for _, mode in self.default_chat_modes.default_chat_modes.items():
            self.chat_modes.update_one(
                {"chat_id": chat_id, "mode_name": mode.name},
                {"$setOnInsert": {"mode_description": mode.description}},
                upsert=True,
            )

    async def create_chat_if_not_exists(self, context: Context) -> None:
        self._init_default_chat_modes(context)

    async def start_chat(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id}, {"$set": {"chat_started": True}}, upsert=True
        )

    async def chat_is_started(self, context: Context) -> bool:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one({"chat_id": chat_id})
        return chat_data.get("chat_started", False)

    async def stop_chat(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id}, {"$set": {"chat_started": False}}
        )

    async def set_language(self, context: Context, language: str) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id}, {"$set": {"language": language}}
        )

    async def get_language(self, context: Context) -> Optional[str]:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one(
            {"chat_id": chat_id}, {"_id": 0, "language": 1}
        )
        return chat_data.get("language")

    async def get_conversation_tracker_state(self, context: Context) -> bool:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one(
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

    async def get_chat_modes(self, context: Context) -> List[ChatModeResponse]:
        chat_id = context.chat_id
        cursor = self.chat_modes.find({"chat_id": chat_id})
        chat_modes = []
        async for doc in cursor:
            chat_modes.append(
                ChatModeResponse(doc["_id"], doc["mode_name"], doc["mode_description"])
            )
        return chat_modes

    async def get_chat_mode(self, context: Context) -> ChatModeResponse:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one(
            {"chat_id": chat_id, "active_mode": True}
        )
        if not chat_data:
            # find the first mode by default
            chat_data = await self.chat_modes.find_one({"chat_id": chat_id})
        return ChatModeResponse(
            chat_data["_id"], chat_data["mode_name"], chat_data["mode_description"]
        )

    async def get_mode_name_by_id(self, context: Context, mode_id: UUID) -> str:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one(
            {"chat_id": chat_id, "_id": ObjectId(mode_id)}
        )
        return chat_data["mode_name"]

    async def set_chat_mode(self, context: Context, mode_id: UUID) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id, "_id": ObjectId(mode_id)},
            {"$set": {"active_mode": True}},
        )

    async def delete_chat_mode(self, context: Context, mode_id: UUID) -> None:
        chat_id = context.chat_id
        await self.chat_modes.delete_one({"chat_id": chat_id, "_id": ObjectId(mode_id)})

    async def add_chat_mode(
        self, context: Context, mode_name: str, mode_description: str
    ) -> None:
        chat_id = context.chat_id
        await self.chat_modes.insert_one(
            {
                "chat_id": chat_id,
                "mode_name": mode_name,
                "mode_description": mode_description,
            }
        )

    async def add_introduction(
        self, context: Context, person: Person, introduction: str
    ) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {"$set": {"introduction": introduction}},
            upsert=True,
        )

    async def add_fact(self, context: Context, person: Person, fact: str) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle}, {"$push": {"facts": fact}}
        )

    async def clear_facts(self, context: Context, person: Person) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle}, {"$set": {"facts": []}}
        )
