from motor.motor_asyncio import AsyncIOMotorDatabase
from collections import namedtuple
from .base_models import BaseModel
from ...models.handlers_input import Person, Context


UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])


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

    async def get_user_usage(self, person: Person) -> UserUsageResponse:
        user_handle = person.user_handle
        usage_data = await self.users.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1, "limit": 1}
        )
        return UserUsageResponse(usage_data.get("usage", 0), usage_data.get("limit", 0))

    async def ban_user(
        self, context: Context, user_handle: str, time_seconds: int
    ) -> None:
        # add timestamp to the user's banned field and set the ban duration
        await self.users.update_one(
            {"handle": user_handle},
            {
                "$set": {
                    "banned": True,
                    "banned_until": context.current_time + time_seconds,
                }
            },
        )

    async def unban_user(self, context: Context, user_handle: str) -> None:
        # remove the banned field from the user
        await self.users.update_one(
            {"handle": user_handle}, {"$unset": {"banned": "", "banned_until": ""}}
        )
