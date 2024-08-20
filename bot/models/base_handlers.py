from abc import ABC, abstractmethod
from typing import Tuple, List, AsyncIterator, Optional, Type
import enum

from .handlers_input import Person, Context, Message
from .handlers_response import (
    CommandResponse,
    LocalizedCommandResponse,
)
from .base_auth import BasePermission


class BaseHandler(ABC):
    permission_classes: Tuple[Type[BasePermission], ...] = ()
    streamable: bool = False

    def __init__(
        self,
    ):
        self._initialized_permissions = self.get_initialized_permissions()

    @abstractmethod
    async def get_initialized_permissions(self) -> List[BasePermission]:
        raise NotImplementedError

    @abstractmethod
    async def get_localized_text(self, text: str, kwargs: dict) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def initialize_context(self, person: Person, context: Context) -> None:
        raise NotImplementedError

    @property
    def permissions(self) -> List[BasePermission]:
        return self._initialized_permissions

    async def is_authenticated(self, person: Person, context: Context) -> bool:
        for permission in self.permissions:
            if not await permission.check(person, context):
                return False
        return True

    async def get_localized_response(
        self, command_response: CommandResponse
    ) -> LocalizedCommandResponse:
        localized_text = (
            None
            if command_response.text is None
            else await self.get_localized_text(
                command_response.text, command_response.kwargs
            )
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=command_response.keyboard
        )

    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        await self.initialize_context(person, context)
        if not await self.is_authenticated(person, context):
            return self.get_localized_response(
                CommandResponse(text="not_authenticated")
            )
        response = await self.get_response(person, context, message, args)
        if response is None:
            return None
        return await self.get_localized_response(response)

    async def stream_handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
        await self.initialize_context(person, context)
        if not await self.is_authenticated(person, context):
            yield self.get_localized_response(CommandResponse(text="not_authenticated"))
            return
        async for chunk in self.stream_get_response(person, context, message, args):
            if chunk is None:
                continue
            yield await self.get_localized_response(chunk)

    @abstractmethod
    async def get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> Optional[CommandResponse]:
        raise NotImplementedError

    async def stream_get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        raise NotImplementedError


class CommandPriority(enum.IntEnum):
    FIRST = 0
    DEFAULT = 1
    ADMIN = 2
    LAST = 3


class BaseCommandHandler(BaseHandler, ABC):
    command: str = None
    list_priority_order: CommandPriority = CommandPriority.DEFAULT

    async def get_localized_description(self) -> str:
        result = await self.get_localized_text(f"{self.command}_description")
        if result is None:
            return await self.get_localized_text("default_command_description")
        return result


class BaseCallbackHandler(BaseHandler, ABC):
    callback_action: str = None


class BaseMessageHandler(BaseHandler, ABC):
    streamable: bool = True

    @abstractmethod
    async def stream_get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        raise NotImplementedError
