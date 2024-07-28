from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Tuple, Union, Literal
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
    ) -> List[Tuple[str, bool, str]]:
        """Get the last N messages from the dialog

        Args:
            context (Context): context object
            last_n (int, optional): amount of messages. Defaults to 10.

        Returns:
            List[Tuple[str, bool, str]]: list of tuples with user_handle, is_bot and message
        """
        chat_id = context.chat_id
        cursor = self.dialogs.find({"chat_id": chat_id}).sort("_id", -1).limit(last_n)
        messages = await cursor.to_list(length=last_n)
        return [
            (msg["user_handle"], msg["is_bot"], msg["message"])
            for msg in reversed(messages)
        ]

    async def add_message_to_dialog(
        self,
        context: Context,
        person: Union[Person, Literal["bot"]],
        message: str,
        timestamp: datetime,
        messages_to_store_limit: int,
    ) -> None:
        chat_id = context.chat_id
        user_handle = "bot" if person == "bot" else person.user_handle

        # Insert the new message
        await self.dialogs.insert_one(
            {
                "chat_id": chat_id,
                "user_handle": user_handle,
                "is_bot": person == "bot",
                "message": message,
                "timestamp": timestamp,
            }
        )

        # Check if the stored messages exceed the limit and delete the oldest if necessary
        current_count = await self.dialogs.count_documents({"chat_id": chat_id})
        if current_count > messages_to_store_limit:
            oldest_message = await self.dialogs.find_one(
                {"chat_id": chat_id}, sort=[("_id", 1)]
            )
            if oldest_message:
                await self.dialogs.delete_one({"_id": oldest_message["_id"]})
