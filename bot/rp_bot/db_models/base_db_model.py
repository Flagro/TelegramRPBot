from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseDBModel:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
