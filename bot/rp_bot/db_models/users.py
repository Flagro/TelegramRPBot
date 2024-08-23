from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_models import BaseModel
from ...models.handlers_input import Person


class Users(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.users = db.users

    async def create_user_if_not_exists(self, person: Person) -> None:
        user_handle = person.user_handle
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$setOnInsert": {
                    "handle": user_handle,
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                }
            },
            upsert=True,
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
            {"handle": user_handle}, {"$unset": {"banned": "", "banned_until": ""}}
        )

    async def is_user_banned(self, user_handle: str) -> bool:
        user_data = await self.users.find_one({"handle": user_handle}, {"banned": 1})
        return user_data.get("banned", False)
