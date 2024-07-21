from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
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
        self.chats = db.chats
        self.chat_modes = db.chat_modes
        self.user_facts = db.user_facts
        self.user_introductions = db.user_introductions
        self.default_chat_modes = default_chat_modes

    def _init_default_chat_modes(self, context: Context) -> None:
        for _, mode in self.default_chat_modes.default_chat_modes.items():
            self.chat_modes.update_one(
                {"chat_id": context.chat_id, "mode_name": mode.name},
                {"$setOnInsert": {"mode_description": mode.description}},
                upsert=True,
            )

    async def create_chat_if_not_exists(
        self, context: Context, default_language: str
    ) -> None:
        """Initialize default parameters for a chat if it does not exist
        Including:
        - initialization of default chat modes
        - initialization of
        - initialization of conversation tracker
        - initialization of language
        - initialization of started chat

        Args:
            context (Context): context of the chat
        """
        self._init_default_chat_modes(context)
        chat_id = context.chat_id
        await self.chats.update_one(
            {"chat_id": chat_id},
            {
                "$setOnInsert": {
                    "chat_id": chat_id,
                    "language": default_language,
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

    async def get_mode_name_by_id(self, context: Context, mode_id: str) -> str:
        chat_id = context.chat_id
        chat_data = await self.chat_modes.find_one(
            {"chat_id": chat_id, "_id": ObjectId(mode_id)}
        )
        return chat_data["mode_name"]

    async def set_chat_mode(self, context: Context, mode_id: str) -> None:
        chat_id = context.chat_id
        await self.chat_modes.update_one(
            {"chat_id": chat_id, "_id": ObjectId(mode_id)},
            {"$set": {"active_mode": True}},
        )

    async def delete_chat_mode(self, context: Context, mode_id: str) -> None:
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
        await self.user_introductions.update_one(
            {"chat_id": chat_id, "user_handle": user_handle},
            {"$set": {"introduction": introduction}},
            upsert=True,
        )

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
