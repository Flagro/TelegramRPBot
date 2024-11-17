from motor.motor_asyncio import AsyncIOMotorDatabase

from ...models.handlers_input import Context, Person


class BaseDBModel:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def create_if_not_exists(self, context: Context, person: Person) -> None:
        pass
