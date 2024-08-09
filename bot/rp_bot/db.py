from motor.motor_asyncio import AsyncIOMotorClient
from ..models.config import DefaultChatModes
from ..models.handlers_input import Person, Context
from .db_models.chats import Chats
from .db_models.user_facts import UserFacts
from .db_models.user_introductions import UserIntroductions
from .db_models.chat_modes import ChatModes
from .db_models.dialogs import Dialogs
from .db_models.users import Users


class DB:
    def __init__(
        self,
        db_uri: str,
        default_language: str,
        default_chat_modes: DefaultChatModes,
        last_n_messages_to_remember: int,
        default_usage_limit: int,
    ):
        client = AsyncIOMotorClient(db_uri)
        db = client.get_default_database()
        self.users = Users(db, default_usage_limit)
        self.chats = Chats(db, default_language)
        self.user_facts = UserFacts(db)
        self.user_introductions = UserIntroductions(db)
        self.chat_modes = ChatModes(db, default_chat_modes)
        self.dialogs = Dialogs(db, last_n_messages_to_remember)

    async def create_if_not_exists(self, person: Person, context: Context) -> None:
        await self.users.create_user_if_not_exists(person)
        await self.chats.create_chat_if_not_exists(context)
        await self.chat_modes.create_chat_modes_if_not_exist(context)
