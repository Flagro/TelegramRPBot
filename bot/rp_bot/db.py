from typing import Optional, List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient
from collections import namedtuple

from ..models.config import DefaultChatModes

UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])
ChatModeResponse = namedtuple(
    "ChatModeResponse", ["id", "mode_name", "mode_description"]
)


class DB:
    def __init__(self,
                 db_user: str,
                 db_password: str,
                 db_host: str,
                 db_port: str,
                 db_name: str,
                 default_chat_modes: DefaultChatModes):
        uri = f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}"
        self.client = AsyncIOMotorClient(uri)
        self.default_chat_modes = default_chat_modes
        self.db = self.client[db_name]
        self.users = self.db.users
        self.chat_modes = self.db.chat_modes
        self.dialogs = self.db.dialogs
        
    def _init_default_chat_modes(self, chat_id: str) -> None:
        for mode in self.default_chat_modes:
            self.chat_modes.update_one(
                {"chat_id": chat_id, "mode_name": mode.name},
                {"$setOnInsert": {"mode_description": mode.description}},
                upsert=True,
            )

    async def create_user_if_not_exists(self, user_handle: str) -> None:
        await self.users.update_one(
            {"handle": user_handle},
            {"$setOnInsert": {"handle": user_handle}},
            upsert=True,
        )

    async def set_language(self, chat_id: str, language: str) -> None:
        await self.chat_modes.update_one(
            {"chat_id": chat_id}, {"$set": {"language": language}}
        )

    async def get_user_usage(self, user_handle: str) -> UserUsageResponse:
        usage_data = await self.users.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1, "limit": 1}
        )
        return UserUsageResponse(usage_data.get("usage", 0), usage_data.get("limit", 0))

    async def get_chat_modes(self, chat_id: str) -> List[ChatModeResponse]:
        cursor = self.chat_modes.find({"chat_id": chat_id})
        chat_modes = []
        async for doc in cursor:
            chat_modes.append(
                ChatModeResponse(doc["_id"], doc["mode_name"], doc["mode_description"])
            )
        return chat_modes

    async def set_chat_mode(self, chat_id: str, mode_id: UUID) -> None:
        await self.chat_modes.update_one(
            {"chat_id": chat_id, "_id": mode_id}, {"$set": {"active_mode": True}}
        )

    async def delete_chat_mode(self, chat_id: str, mode_id: UUID) -> None:
        await self.chat_modes.delete_one({"chat_id": chat_id, "_id": mode_id})

    async def add_chat_mode(
        self, chat_id: str, mode_name: str, mode_description: str
    ) -> None:
        await self.chat_modes.insert_one(
            {
                "chat_id": chat_id,
                "mode_name": mode_name,
                "mode_description": mode_description,
            }
        )

    async def add_introduction(
        self, chat_id: str, user_handle: str, introduction: str
    ) -> None:
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {"$set": {"introduction": introduction}},
            upsert=True,
        )

    async def add_fact(self, chat_id: str, user_handle: str, fact: str) -> None:
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle}, {"$push": {"facts": fact}}
        )

    async def clear_facts(self, chat_id: str, user_handle: str) -> None:
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle}, {"$set": {"facts": []}}
        )

    async def reset(self, chat_id: str) -> None:
        await self.dialogs.delete_many({"chat_id": chat_id})

    async def save_thread_message(
        self, thread_id: Optional[str], user_handle: str, message: str
    ) -> None:
        await self.dialogs.update_one(
            {"thread_id": thread_id, "user_handle": user_handle},
            {"$push": {"messages": message}},
            upsert=True,
        )

    async def add_user_input_to_dialog(
        self,
        chat_id: str,
        user_handle: str,
        message: str,
        image_description: str,
        voice_description: str,
    ) -> None:
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {
                "$push": {
                    "dialog": {
                        "message": message,
                        "image_description": image_description,
                        "voice_description": voice_description,
                    }
                }
            },
            upsert=True,
        )

    async def add_bot_response_to_dialog(
        self, chat_id: str, bot_response: str, response_image_url: str
    ) -> None:
        await self.dialogs.update_one(
            {"chat_id": chat_id},
            {
                "$push": {
                    "dialog": {
                        "bot_response": bot_response,
                        "response_image_url": response_image_url,
                    }
                }
            },
        )
