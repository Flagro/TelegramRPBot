from abc import ABC, abstractmethod
from typing import List, Optional

from .db import DB
from ai_agent.ai import AI
from ai_agent.moderation import moderate_user_message
from .prompt_manager import PromptManager
from .auth import Auth
from .localizer import Localizer
from ..models.config import BotConfig
from ..models.base_handlers import (
    BaseCommandHandler,
    BaseCallbackHandler,
    BaseMessageHandler,
)
from ..models.base_auth import BasePermission
from ..models.handlers_input import Person, Context, Message


class RPBotHandlerMixin(ABC):
    def __init__(
        self,
        db: DB,
        ai: AI,
        localizer: Localizer,
        prompt_manager: PromptManager,
        auth: Auth,
        bot_config: BotConfig,
        *args,
        **kwargs
    ):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.prompt_manager = prompt_manager
        self.auth = auth
        self.bot_config = bot_config
        super().__init__(*args, **kwargs)

    @property
    @abstractmethod
    def permission_classes(self) -> List[BasePermission]:
        raise NotImplementedError

    def get_initialized_permissions(self) -> List[BasePermission]:
        result = []
        for permission_class in self.permission_classes:
            result.append(permission_class(self.auth))
        return result

    async def moderate_message(self, message: Message) -> bool:
        return moderate_user_message(message)

    async def get_localized_text(
        self, text: str, kwargs: Optional[dict] = None, context: Optional[Context] = None
    ) -> Optional[str]:
        return await self.localizer.get_command_response(
            text=text, kwargs=kwargs, context=context
        )

    async def initialize_context(self, person: Person, context: Context) -> None:
        await self.db.create_if_not_exists(person, context)


class RPBotCommandHandler(RPBotHandlerMixin, BaseCommandHandler, ABC):
    pass


class RPBotCallbackHandler(RPBotHandlerMixin, BaseCallbackHandler, ABC):
    pass


class RPBotMessageHandler(RPBotHandlerMixin, BaseMessageHandler, ABC):
    pass
