from abc import ABC, abstractmethod
from typing import List, AsyncIterator, Optional
import logging
import enum

# TODO: base handlers should be moved to the bot package
from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from ..rp_bot.prompt_manager import PromptManager
from ..rp_bot.auth import Auth, BasePermission

from .localizer import Localizer
from .handlers_input import Person, Context, Message
from .handlers_response import (
    CommandResponse,
    LocalizedCommandResponse,
)
from .config import BotConfig


class BaseHandler(ABC):
    permissions: List[BasePermission] = []
    streamable: bool = False

    def __init__(
        self,
        db: DB,
        ai: AI,
        localizer: Localizer,
        prompt_manager: PromptManager,
        auth: Auth,
        bot_config: BotConfig,
    ):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.prompt_manager = prompt_manager
        self.auth = auth
        self.bot_config = bot_config
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

    async def is_authenticated(self, person: Person, context: Context) -> bool:
        for permission in self.permissions:
            initialized_permission = permission(self.auth)
            if not await initialized_permission.check(person, context):
                return False
        return True

    async def handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> LocalizedCommandResponse:
        await self.db.create_if_not_exists(person, context)
        if not await self.is_authenticated(person, context):
            response = CommandResponse(text="not_authenticated")
        else:
            response = await self.get_response(person, context, message, args)
        if response is None:
            return None
        localized_text = (
            None
            if response.text is None
            else await self.localizer.get_command_response(
                response.text, response.kwargs
            )
        )
        return LocalizedCommandResponse(
            localized_text=localized_text, keyboard=response.keyboard
        )

    async def stream_handle(
        self, person: Person, context: Context, message: Message, args: List[str]
    ) -> AsyncIterator[LocalizedCommandResponse]:
        await self.db.create_if_not_exists(person, context)
        if not await self.is_authenticated(person, context):
            yield LocalizedCommandResponse(
                localized_text=await self.localizer.get_command_response(
                    "not_authenticated"
                ),
                keyboard=None,
            )
            return
        async for chunk in self.stream_get_response(person, context, message, args):
            if chunk is None:
                continue
            localized_text = (
                None
                if chunk.text is None
                else await self.localizer.get_command_response(chunk.text, chunk.kwargs)
            )
            yield LocalizedCommandResponse(
                localized_text=localized_text,
                keyboard=chunk.keyboard,
            )

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
        result = await self.localizer.get_command_response(
            f"{self.command}_description"
        )
        if result is None:
            return await self.localizer.get_command_response(
                "default_command_description"
            )
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
