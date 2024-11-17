from typing import List
from pydantic import BaseModel
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


from .base_db_model import BaseDBModel
from ...models.config import DefaultChatModes
from ...models.handlers_input import Context, Person


class ChatModeResponse(BaseModel):
    id: ObjectId
    mode_name: str
    mode_description: str


class ChatModes(BaseDBModel):
    def __init__(
        self, db: AsyncIOMotorDatabase, default_chat_modes: DefaultChatModes
    ) -> None:
        super().__init__(db)
        self.chat_modes = db.chat_modes
        self.default_chat_modes = default_chat_modes

    async def create_chat_modes_if_not_exist(
        self, person: Person, context: Context
    ) -> None:
        for _, mode in self.default_chat_modes.default_chat_modes.items():
            self.chat_modes.update_one(
                {"chat_id": context.chat_id, "mode_name": mode.name},
                {"$setOnInsert": {"mode_description": mode.description}},
                upsert=True,
            )

    async def get_chat_modes(self, context: Context) -> List[ChatModeResponse]:
        cursor = self.chat_modes.find({"chat_id": context.chat_id})
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

    async def get_mode_name_by_id(self, context: Context, mode_id: str) -> str:
        chat_data = await self.chat_modes.find_one(
            {"chat_id": context.chat_id, "_id": ObjectId(mode_id)}
        )
        return chat_data["mode_name"]

    async def set_chat_mode(self, context: Context, mode_id: str) -> None:
        await self.chat_modes.update_one(
            {"chat_id": context.chat_id, "_id": ObjectId(mode_id)},
            {"$set": {"active_mode": True}},
        )

    async def delete_chat_mode(self, context: Context, mode_id: str) -> None:
        await self.chat_modes.delete_one(
            {"chat_id": context.chat_id, "_id": ObjectId(mode_id)}
        )

    async def add_chat_mode(
        self, context: Context, mode_name: str, mode_description: str
    ) -> None:
        await self.chat_modes.insert_one(
            {
                "chat_id": context.chat_id,
                "mode_name": mode_name,
                "mode_description": mode_description,
            }
        )
