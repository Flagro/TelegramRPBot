from abc import ABC, abstractmethod
from typing import List, Optional
from omnimodkit.models_toolkit import ModelsToolkit
from .db import DB
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
from ..models.handlers_input import Person, Context


class RPBotHandlerMixin(ABC):
    def __init__(
        self,
        db: DB,
        models_toolkit: ModelsToolkit,
        localizer: Localizer,
        prompt_manager: PromptManager,
        auth: Auth,
        bot_config: BotConfig,
        *args,
        **kwargs
    ):
        self.db = db
        self.models_toolkit = models_toolkit
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

    async def get_localized_text(
        self,
        text: str,
        kwargs: Optional[dict] = None,
        context: Optional[Context] = None,
    ) -> Optional[str]:
        return await self.localizer.get_command_response(
            text=text, kwargs=kwargs, context=context
        )

    async def initialize_context(self, person: Person, context: Context) -> None:
        await self.db.create_if_not_exists(person, context)
        await self.db.update_if_needed(person, context)


class RPBotCommandHandler(RPBotHandlerMixin, BaseCommandHandler, ABC):
    pass


class RPBotCallbackHandler(RPBotHandlerMixin, BaseCallbackHandler, ABC):
    pass


class RPBotMessageHandler(RPBotHandlerMixin, BaseMessageHandler, ABC):
    pass
