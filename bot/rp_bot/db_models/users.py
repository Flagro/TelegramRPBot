from motor.motor_asyncio import AsyncIOMotorDatabase
from collections import namedtuple
from datetime import datetime
from .base_models import BaseModel
from ...models.handlers_input import Person, Context


UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])


class Users(BaseModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.users = db.users

    async def create_user_if_not_exists(self, person: Person, usage_limit: int) -> None:
        user_handle = person.user_handle
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$setOnInsert": {
                    "handle": user_handle,
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                    "usage": 0,
                    "limit": usage_limit,
                }
            },
            upsert=True,
        )

    async def add_usage_points(self, person: Person, points: int) -> None:
        user_handle = person.user_handle
        await self.users.update_one(
            {"handle": user_handle}, {"$inc": {"usage": points}}
        )

    async def get_user_usage(self, person: Person) -> UserUsageResponse:
        user_handle = person.user_handle
        usage_data = await self.users.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1, "limit": 1}
        )
        return UserUsageResponse(usage_data.get("usage", 0), usage_data.get("limit", 0))

    async def get_user_usage_limit(self, person: Person) -> int:
        user_handle = person.user_handle
        usage_data = await self.users.find_one(
            {"handle": user_handle}, {"_id": 0, "limit": 1}
        )
        return usage_data.get("limit", 0)

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
