from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseModel:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
