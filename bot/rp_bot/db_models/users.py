from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import telegram

from .base_db_model import BaseDBModel
from ...models.handlers_input import Person, Context


class Users(BaseDBModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.users = db.users

    async def create_if_not_exists(self, person: Person, context: Context) -> None:
        user_handle = person.user_handle
        # TODO: think about passing the whole person object
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$setOnInsert": {
                    "telegram_id": person.telegram_id,
                    "handle": user_handle,
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                }
            },
            upsert=True,
        )

    async def get_person_by_handle(self, user_handle: str) -> Person:
        user_data = await self.users.find_one({"handle": user_handle})
        telegram_id = user_data.get(
            "telegram_id", -1
        )  # -1 is a placeholder for no telegram_id
        user_first_name = user_data.get("first_name", "")
        user_last_name = user_data.get("last_name", "")
        return Person(
            telegram_id=telegram_id,
            user_handle=user_handle,
            first_name=user_first_name,
            last_name=user_last_name,
        )

    async def ban_user(self, user_handle: str, time_seconds: int) -> None:
        # add timestamp to the user's banned field and set the ban duration
        current_timestamp = datetime.now().timestamp()
        banned_until = current_timestamp + time_seconds
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$set": {
                    "banned": True,
                    "banned_until": banned_until,
                }
            },
        )

    async def unban_user(self, user_handle: str) -> None:
        # remove the banned field from the user
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$unset": {
                    "banned": "",
                    "banned_until": "",
                }
            },
        )

    async def is_user_banned(self, user_handle: str) -> bool:
        user_data = await self.users.find_one({"handle": user_handle}, {"banned": 1})
        return user_data.get("banned", False)

    async def has_accepted_terms(self, user_handle: str) -> bool:
        user_data = await self.users.find_one(
            {"handle": user_handle}, {"accepted_terms": 1}
        )
        return user_data.get("accepted_terms", False)

    async def has_declined_terms(self, user_handle: str) -> bool:
        user_data = await self.users.find_one(
            {"handle": user_handle}, {"declined_terms": 1}
        )
        return user_data.get("declined_terms", False)

    async def accept_terms(self, user_handle: str) -> None:
        """Accept terms for a user and clear any previous decline"""
        await self.users.update_one(
            {"handle": user_handle},
            {"$set": {"accepted_terms": True}, "$unset": {"declined_terms": ""}},
            upsert=True,
        )

    async def decline_terms(self, user_handle: str) -> None:
        """Decline terms for a user and clear any previous acceptance"""
        await self.users.update_one(
            {"handle": user_handle},
            {"$set": {"declined_terms": True}, "$unset": {"accepted_terms": ""}},
            upsert=True,
        )

    async def clear_user_data(self, user_handle: str) -> None:
        # Nullify first and last name for the handle
        # TODO: move banned and terms status to their own tables
        # so we can delete all the data here
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$unset": {
                    "first_name": "",
                    "last_name": "",
                }
            },
        )
