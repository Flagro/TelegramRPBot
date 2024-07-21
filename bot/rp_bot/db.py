from motor.motor_asyncio import AsyncIOMotorClient
from ..models.config import DefaultChatModes
from .db_models.chats import Chats
from .db_models.dialogs import Dialogs
from .db_models.users import Users


class DB:
    def __init__(
        self,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: str,
        db_name: str,
        default_chat_modes: DefaultChatModes,
    ):
        uri = f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}"
        client = AsyncIOMotorClient(uri)
        db = client[db_name]
        self.users = Users(db)
        self.chats = Chats(db, default_chat_modes)
        self.dialogs = Dialogs(db)
