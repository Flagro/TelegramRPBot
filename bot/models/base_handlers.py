from abc import ABC, abstractmethod
from functools import wraps
from typing import List
import logging

from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from .localizer import Localizer
from ..rp_bot.auth import Auth
from ..models.handlers_input import Person, Context, Message
from ..models.handlers_response import CommandResponse, LocalizedCommandResponse


def is_authenticated(func):
    @wraps(func)
    async def wrapper(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        for permission in self.permissions:
            if not permission()(person, context, self.auth):
                return CommandResponse("not_authenticated", {})
        await self.db.create_user_if_not_exists(person)
        await self.db.create_chat_if_not_exists(context)
        return await func(self, person, context, message, args)

    return wrapper


class BaseHandler(ABC):
    permissions: list = []

    def __init__(self, db: DB, ai: AI, localizer: Localizer, auth: Auth):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.auth = auth
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

    @abstractmethod
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        raise NotImplementedError


class BaseCommandHandler(BaseHandler, ABC):
    command: str = None
    list_priority_order: int = 0

    def get_localized_description(self) -> str:
        return self.localizer.get_command_response(f"{self.command}_description", {})

    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        command_response = await self.get_command_response(
            person, context, message, args
        )
        return command_response

    @abstractmethod
    async def get_command_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        raise NotImplementedError


class BaseCallbackHandler(BaseHandler, ABC):
    callback_action: str = None

    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        callback_response = await self.get_callback_response(
            person, context, message, args
        )
        return callback_response

    @abstractmethod
    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        raise NotImplementedError


class BaseMessageHandler(BaseHandler, ABC):
    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        message_response = await self.get_reply(person, context, message, args)
        return message_response

    @abstractmethod
    async def get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        raise NotImplementedError
