from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from ..models.config import DefaultChatModes
from ..models.handlers_input import Person, Context
from .db_models.chats import Chats
from .db_models.user_facts import UserFacts
from .db_models.user_introductions import UserIntroductions
from .db_models.chat_modes import ChatModes
from .db_models.dialogs import Dialogs
from .db_models.users import Users
from .db_models.user_usage import UserUsage


class DB:
    def __init__(
        self,
        db_uri: str,
        default_language: str,
        default_chat_modes: DefaultChatModes,
        last_n_messages_to_remember: int,
        last_n_messages_to_store: Optional[int],
        default_usage_limit: int,
    ):
        client = AsyncIOMotorClient(db_uri)
        db = client.get_default_database()
        self.users = Users(db)
        self.user_usage = UserUsage(db, default_usage_limit)
        self.chats = Chats(db, default_language)
        self.user_facts = UserFacts(db)
        self.user_introductions = UserIntroductions(db)
        self.chat_modes = ChatModes(db, default_chat_modes)
        self.dialogs = Dialogs(
            db, last_n_messages_to_remember, last_n_messages_to_store
        )
        # TODO: deduplicate this
        self.models = [
            self.users,
            self.user_usage,
            self.chats,
            self.user_facts,
            self.user_introductions,
            self.chat_modes,
            self.dialogs,
        ]

    async def create_if_not_exists(self, person: Person, context: Context) -> None:
        for model in self.models:
            await model.create_if_not_exists(person, context)

    async def update_if_needed(self, person: Person) -> None:
        # TODO: unify update logic
        await self.user_usage.update_usage_if_needed(person)
