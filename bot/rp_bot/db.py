from typing import Optional, List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient
from collections import namedtuple

from ..models.config import DefaultChatModes
from ..models.handlers_input import Person, Context, Message


UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])
ChatModeResponse = namedtuple(
    "ChatModeResponse", ["id", "mode_name", "mode_description"]
)


class DB:
    def __init__(
        self,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: str,
        db_name: str,
        default_chat_modes: DefaultChatModes,
    ):
        uri = f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}"
        self.client = AsyncIOMotorClient(uri)
        self.default_chat_modes = default_chat_modes
        self.db = self.client[db_name]
        self.users = self.db.users
        self.chat_modes = self.db.chat_modes
        self.dialogs = self.db.dialogs

    def _init_default_chat_modes(self, context: Context) -> None:
        chat_id = context.chat_id
        for mode in self.default_chat_modes:
            self.chat_modes.update_one(
                {"chat_id": chat_id, "mode_name": mode.name},
                {"$setOnInsert": {"mode_description": mode.description}},
                upsert=True,
            )

    async def create_user_if_not_exists(self, person: Person) -> None:
        user_handle = person.user_handle
        await self.users.update_one(
            {"handle": user_handle},
            {"$setOnInsert": {"handle": user_handle}},
            upsert=True,
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

    async def get_user_usage(self, person: Person) -> UserUsageResponse:
        user_handle = person.user_handle
        usage_data = await self.users.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1, "limit": 1}
        )
        return UserUsageResponse(usage_data.get("usage", 0), usage_data.get("limit", 0))

    async def get_chat_modes(self, context: Context) -> List[ChatModeResponse]:
        chat_id = context.chat_id
        cursor = self.chat_modes.find({"chat_id": chat_id})
        chat_modes = []
        async for doc in cursor:
            chat_modes.append(
                ChatModeResponse(doc["_id"], doc["mode_name"], doc["mode_description"])
            )
        return chat_modes

    async def set_chat_mode(self, context: Context, mode_id: UUID) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id, "_id": mode_id}, {"$set": {"active_mode": True}}
        )

    async def delete_chat_mode(self, context: Context, mode_id: UUID) -> None:
        chat_id = context.chat_id
        await self.chat_modes.delete_one({"chat_id": chat_id, "_id": mode_id})

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

    async def reset(self, context: Context) -> None:
        chat_id = context.chat_id
        await self.dialogs.delete_many({"chat_id": chat_id})

    async def get_messages(self, context: Context, last_n: int = 10) -> List[str]:
        chat_id = context.chat_id
        cursor = self.dialogs.find(
            {"chat_id": chat_id},
            {"_id": 0, "messages": {"$slice": -last_n}},
        )
        messages = []
        async for doc in cursor:
            messages.extend(doc.get("messages", []))
        return messages

    async def save_thread_message(
        self, context: Context, person: Person, message: str
    ) -> None:
        thread_id = context.thread_id
        user_handle = person.user_handle
        await self.dialogs.update_one(
            {"thread_id": thread_id, "user_handle": user_handle},
            {"$push": {"messages": message}},
            upsert=True,
        )

    async def add_user_input_to_dialog(
        self,
        context: Context,
        person: Person,
        message: Message,
        image_description: str,
        voice_description: str,
    ) -> None:
        chat_id = context.chat_id
        user_handle = person.user_handle
        message_text = message.message_text
        await self.dialogs.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {
                "$push": {
                    "dialog": {
                        "message": message_text,
                        "image_description": image_description,
                        "voice_description": voice_description,
                    }
                }
            },
            upsert=True,
        )

    async def add_bot_response_to_dialog(
        self, context: Context, bot_response: str, response_image_url: str
    ) -> None:
        chat_id = context.chat_id
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
