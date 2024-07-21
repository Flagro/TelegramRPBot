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
