from abc import ABC, abstractmethod
from functools import wraps
from typing import List, AsyncIterator
import logging

from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from .localizer import Localizer
from ..rp_bot.auth import Auth
from ..models.handlers_input import Person, Context, Message
from ..models.handlers_response import (
    CommandResponse,
    LocalizedCommandResponse,
)
from ..models.config import BotConfig


def is_authenticated(func):
    @wraps(func)
    async def wrapper(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        for permission in self.permissions:
            if not permission()(person, context, self.auth):
                localized_text = self.localizer.get_command_response(
                    "not_authenticated", {}
                )
                return LocalizedCommandResponse(localized_text=localized_text)
        await self.db.users.create_user_if_not_exists(person)
        await self.db.chats.create_chat_if_not_exists(
            context, default_language=self.bot_config.default_language
        )
        return await func(self, person, context, message, args)

    return wrapper


def stream_is_authenticated(func):
    @wraps(func)
    async def wrapper(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
        for permission in self.permissions:
            if not permission()(person, context, self.auth):
                localized_text = self.localizer.get_command_response(
                    "not_authenticated", {}
                )
                yield LocalizedCommandResponse(localized_text=localized_text)
                return
        await self.db.users.create_user_if_not_exists(person)
        await self.db.chats.create_chat_if_not_exists(
            context, default_language=self.bot_config.default_language
        )
        async for chunk in func(self, person, context, message, args):
            yield chunk

    return wrapper


class BaseHandler(ABC):
    permissions: list = []
    streamable: bool = False

    def __init__(
        self, db: DB, ai: AI, localizer: Localizer, auth: Auth, bot_config: BotConfig
    ):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.auth = auth
        self.bot_config = bot_config
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

    @abstractmethod
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        raise NotImplementedError

    async def stream_handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
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
        localized_text = self.localizer.get_command_response(
            command_response.text, command_response.kwargs
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=command_response.keyboard
        )

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
        localized_text = self.localizer.get_command_response(
            callback_response.text, callback_response.kwargs
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=callback_response.keyboard
        )

    @abstractmethod
    async def get_callback_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        raise NotImplementedError


class BaseMessageHandler(BaseHandler, ABC):
    streamable: bool = True

    @is_authenticated
    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        message_response = await self.get_reply(person, context, message, args)
        localized_text = self.localizer.get_command_response(
            message_response.text, message_response.kwargs
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=message_response.keyboard
        )

    @stream_is_authenticated
    async def stream_handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
        async for chunk in self.stream_get_reply(person, context, message, args):
            localized_text = self.localizer.get_command_response(
                chunk.text, chunk.kwargs
            )
            yield LocalizedCommandResponse(
                localized_text=localized_text,
                keyboard=chunk.keyboard,
            )

    @abstractmethod
    async def get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> CommandResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream_get_reply(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        raise NotImplementedError
