from abc import ABC, abstractmethod
from functools import wraps
from typing import List
import logging

from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from .localizer import Localizer
from ..rp_bot.auth import Auth
from ..models.handlers_input import Person, Context, Message
from ..models.handlers_response import CommandResponse
from ..models.config import BotConfig


def is_authenticated(func):
    @wraps(func)
    async def wrapper(self, person: Person, context: Context, message: Message, args: List[str]):
        for permission in self.permissions:
            if not permission()(person, context, self.auth):
                return CommandResponse("not_authenticated", {})
        await self.db.create_user_if_not_exists(person)
        return await func(self, person, context, message, args)
    
    return wrapper


class BaseHandler(ABC):
    permissions: list = []

    def __init__(self, db: DB, ai: AI, localizer: Localizer, auth: Auth, bot_config: BotConfig):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.auth = auth
        self.bot_config = bot_config
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

    @abstractmethod
    async def handle(self, person: Person, context: Context, message: Message, args: List[str]):
        raise NotImplementedError


class BaseCommandHandler(BaseHandler, ABC):
    command: str = None
    list_priority_order: int = 0

    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        command_response = await self.get_command_response(person, context, message, args)
        return command_response

    @abstractmethod
    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        raise NotImplementedError


class BaseCallbackHandler(BaseHandler, ABC):
    callback_action: str = None

    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        callback_response = await self.get_callback_response(person, context, message, args)
        return callback_response

    @abstractmethod
    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        raise NotImplementedError


class BaseMessageHandler(BaseHandler, ABC):
    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        message_response = await self.get_reply(person, context, message, args)
        return message_response

    @abstractmethod
    async def get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ):
        raise NotImplementedError
