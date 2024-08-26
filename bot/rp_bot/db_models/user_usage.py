from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_db_model import BaseDBModel
from ...models.handlers_input import Person


class UserUsageResponse(BaseModel):
    this_month_usage: int
    limit: int


class UserUsage(BaseDBModel):
    def __init__(self, db: AsyncIOMotorDatabase, default_usage_limit: int) -> None:
        super().__init__(db)
        self.user_usage = db.user_usage
        self.default_usage_limit = default_usage_limit

    async def update_usage_if_needed(self, person: Person) -> None:
        """
        Initialize user usage with 0 and last_reset with the current date.
        If the current date is after the last_reset date, reset the usage to 0.
        TODO: this logic should be flexible to allow for different reset periods.
        """
        user_handle = person.user_handle
        current_date = datetime.now().date()
        user_data = await self.user_usage.find_one({"handle": user_handle})
        if user_data is None:
            await self.user_usage.insert_one(
                {"handle": user_handle, "usage": 0, "limit": self.default_usage_limit}
            )
        else:
            last_reset = user_data.get("last_reset", current_date)
            if current_date > last_reset:
                await self.user_usage.update_one(
                    {"handle": user_handle},
                    {"$set": {"usage": 0, "last_reset": current_date}},
                )

    async def add_usage_points(self, person: Person, points: int) -> None:
        user_handle = person.user_handle
        await self.user_usage.update_one(
            {"handle": user_handle}, {"$inc": {"usage": points}}
        )

    async def get_user_usage(self, person: Person) -> int:
        user_handle = person.user_handle
        usage_data = await self.user_usage.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1}
        )
        return usage_data.get("usage", 0)

    async def get_user_usage_report(self, person: Person) -> UserUsageResponse:
        user_handle = person.user_handle
        usage_data = await self.user_usage.find_one(
            {"handle": user_handle}, {"_id": 0, "usage": 1, "limit": 1}
        )
        return UserUsageResponse(usage_data.get("usage", 0), usage_data.get("limit", 0))

    async def get_user_usage_limit(self, person: Person) -> int:
        user_handle = person.user_handle
        usage_data = await self.user_usage.find_one(
            {"handle": user_handle}, {"_id": 0, "limit": 1}
        )
        return usage_data.get("limit", 0)
