import enum
from abc import ABC, abstractmethod
from typing import Tuple, List, AsyncIterator, Optional, Type
from logging import Logger

from .handlers_input import Person, Context, Message
from .handlers_response import (
    CommandResponse,
    LocalizedCommandResponse,
)
from .base_auth import BasePermission
from .base_moderation import ModerationError


class BaseHandler(ABC):
    permission_classes: Tuple[Type[BasePermission], ...] = ()
    streamable: bool = False

    def __init__(
        self,
        logger: Logger,
    ):
        self.logger = logger
        self._initialized_permissions = self.get_initialized_permissions()

    @abstractmethod
    def get_initialized_permissions(self) -> List[BasePermission]:
        raise NotImplementedError

    @abstractmethod
    async def get_localized_text(
        self,
        text: str,
        kwargs: Optional[dict] = None,
        context: Optional[Context] = None,
    ) -> Optional[str]:
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
                handler_name = str(self)
                permission_name = permission.__class__.__name__
                self.logger.info(
                    f"User {person.user_handle} does not have permission to use "
                    f"{handler_name}. Permission: {permission_name}"
                )
                return False
        return True

    async def get_localized_response(
        self, command_response: CommandResponse, context: Optional[Context] = None
    ) -> LocalizedCommandResponse:
        localized_text = (
            None
            if command_response.text is None
            else await self.get_localized_text(
                text=command_response.text,
                kwargs=command_response.kwargs,
                context=context,
            )
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=command_response.keyboard
        )

    async def _log_handler_request(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> None:
        handler_name = str(self)
        user_handle = person.user_handle
        chat_id = context.chat_id
        message_details = (
            f" with message of length {len(message.text)}" if message.text else ""
        )
        args_prompt = " with args: " + " ".join(args) if args else ""
        self.logger.info(
            f"Handling request for {handler_name} in chat {chat_id} "
            f"by user {user_handle}{message_details}{args_prompt}"
        )

    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        await self.initialize_context(person, context)
        if not await self.is_authenticated(person, context):
            return self.get_localized_response(
                CommandResponse(text="not_authenticated"), context
            )
        await self._log_handler_request(person, context, message, args)
        try:
            response = await self.get_response(person, context, message, args)
        except ModerationError as moderation_error:
            response = CommandResponse(
                text="message_moderation_failed",
                kwargs={"moderation_reason": str(moderation_error)},
            )
        if response is None:
            return None
        return await self.get_localized_response(response, context)

    async def stream_handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
        await self.initialize_context(person, context)
        if not await self.is_authenticated(person, context):
            chunk = CommandResponse(text="not_authenticated")
            yield await self.get_localized_response(chunk, context)
            return
        await self._log_handler_request(person, context, message, args)
        try:
            async for chunk in self.stream_get_response(person, context, message, args):
                if chunk is None:
                    continue
                yield await self.get_localized_response(chunk, context)
        except ModerationError as moderation_error:
            chunk = CommandResponse(
                text="message_moderation_failed",
                kwargs={"moderation_reason": str(moderation_error)},
            )
            yield await self.get_localized_response(chunk, context)
            return

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

    def __str__(self):
        return f"Command Handler: {self.command}"

    async def get_localized_description(self, context: Optional[Context] = None) -> str:
        result = await self.get_localized_text(
            text=f"{self.command}_description", context=context
        )
        if result is None:
            return await self.get_localized_text(
                text="default_command_description", context=context
            )
        return result


class BaseCallbackHandler(BaseHandler, ABC):
    callback_action: str = None

    def __str__(self):
        return f"Callback Handler: {self.callback_action}"


class BaseMessageHandler(BaseHandler, ABC):
    streamable: bool = True

    def __str__(self):
        return "Message Handler"

    @abstractmethod
    async def stream_get_response(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[CommandResponse]:
        raise NotImplementedError
