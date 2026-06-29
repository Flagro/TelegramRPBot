from typing import List, Tuple, Union, Literal, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_db_model import BaseDBModel
from ...models.handlers_input import Person, Context, TranscribedMessage
from ..memory_utils import build_scope_key, get_participant_key


class Dialogs(BaseDBModel):
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        last_n_messages_to_remember: int,
        last_n_messages_to_store: Optional[int],
    ) -> None:
        super().__init__(db)
        self.dialogs = db.dialogs
        self.last_n_messages_to_remember = last_n_messages_to_remember
        self.last_n_messages_to_store = last_n_messages_to_store

    async def reset(self, context: Context) -> None:
        await self.dialogs.delete_many({"chat_id": context.chat_id})

    async def get_messages(
        self, context: Context
    ) -> List[Tuple[str, bool, TranscribedMessage]]:
        """Get the last N messages from the dialog

        Args:
            context (Context): context object
            last_n (int, optional): amount of messages. Defaults to 10.

        Returns:
            List[Tuple[str, bool, TranscribedMessage]]: list of tuples with user_handle, is_bot and message
        """
        cursor = (
            self.dialogs.find({"chat_id": context.chat_id})
            .sort("_id", -1)
            .limit(self.last_n_messages_to_remember)
        )
        messages = await cursor.to_list(length=self.last_n_messages_to_remember)
        return [
            (
                msg["user_handle"],
                msg["is_bot"],
                TranscribedMessage(
                    message_text=msg.get("message_text"),
                    timestamp=msg["timestamp"],
                    image_description=msg.get("image_description"),
                    voice_description=msg.get("voice_description"),
                ),
            )
            for msg in reversed(messages)
        ]

    async def add_message_to_dialog(
        self,
        context: Context,
        person: Union[Person, Literal["bot"]],
        transcribed_message: TranscribedMessage,
        scope_key: Optional[str] = None,
        memory_role: Optional[str] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        chat_id = context.chat_id
        user_handle = "bot" if person == "bot" else person.user_handle
        participant_key = None if person == "bot" else get_participant_key(person)
        telegram_user_id = None if person == "bot" else person.telegram_id

        # Insert the new message
        document = {
            "chat_id": chat_id,
            "thread_id": context.thread_id,
            "scope_key": scope_key or build_scope_key(context),
            "user_handle": user_handle,
            "telegram_user_id": telegram_user_id,
            "participant_key": participant_key,
            "is_bot": person == "bot",
            "memory_role": memory_role or ("assistant" if person == "bot" else "user"),
            "message_text": transcribed_message.message_text,
            "image_description": transcribed_message.image_description,
            "voice_description": transcribed_message.voice_description,
            "timestamp": transcribed_message.timestamp,
        }
        if provider_metadata:
            document["provider_metadata"] = provider_metadata
        await self.dialogs.insert_one(document)

        # Check if the stored messages exceed the limit and delete the oldest if necessary
        while (
            self.last_n_messages_to_store is not None
            and await self.dialogs.count_documents({"chat_id": chat_id})
            > self.last_n_messages_to_store
        ):
            oldest_message = await self.dialogs.find_one(
                {"chat_id": chat_id}, sort=[("_id", 1)]
            )
            if oldest_message:
                await self.dialogs.delete_one({"_id": oldest_message["_id"]})

    async def clear_user_data(self, user_handle: str) -> None:
        await self.dialogs.delete_many({"user_handle": user_handle})

    async def search_recent_dialog(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
        limit: int = 6,
    ) -> List[str]:
        filters: Dict[str, Any] = {"chat_id": context.chat_id}
        if context.thread_id is not None:
            filters["thread_id"] = context.thread_id
        if participant_key:
            filters["participant_key"] = participant_key
        if query:
            filters["message_text"] = {"$regex": query, "$options": "i"}

        cursor = self.dialogs.find(filters).sort("_id", -1).limit(limit)
        messages = await cursor.to_list(length=limit)
        result = []
        for msg in reversed(messages):
            message_text = msg.get("message_text") or ""
            if not message_text:
                continue
            result.append(f"{msg.get('user_handle', 'unknown')}: {message_text}")
        return result
