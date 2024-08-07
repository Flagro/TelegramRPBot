from typing import List
from logging import Logger
from bot.models.base_handlers import (
    BaseCallbackHandler,
    BaseCommandHandler,
    BaseMessageHandler,
)
from ..models.base_bot import BaseBot
from .commands import handlers as command_handlers
from .callbacks import handlers as callback_handlers
from .messages import handlers as message_handlers
from .ai import AI
from .db import DB
from .auth import Auth
from ..models.localizer import Localizer
from ..models.config import (
    BotConfig,
    DefaultChatModes,
    LocalizerTranslations,
    AIConfig,
)


class RPBot(BaseBot):
    def __init__(
        self,
        db_uri: str,
        openai_api_key: str,
        translations: LocalizerTranslations,
        default_chat_modes: DefaultChatModes,
        ai_config: AIConfig,
        bot_config: BotConfig,
        allowed_handles: List[str],
        admin_handles: List[str],
        logger: Logger,
    ):
        self.db = DB(
            db_uri=db_uri,
            default_language=bot_config.default_language,
            default_chat_modes=default_chat_modes,
            last_n_messages_to_remember=bot_config.last_n_messages_to_remember,
            default_usage_limit=bot_config.default_usage_limit,
        )
        self.ai = AI(openai_api_key=openai_api_key, db=self.db, ai_config=ai_config)
        self.localizer = Localizer(
            translations=translations, default_language=bot_config.default_language
        )
        self.auth = Auth(
            allowed_handles=allowed_handles,
            admin_handles=admin_handles,
            db=self.db,
        )
        self.bot_config = bot_config
        self.logger = logger

    def _init_handler(self, handler):
        return handler(
            db=self.db,
            ai=self.ai,
            localizer=self.localizer,
            auth=self.auth,
            bot_config=self.bot_config,
        )

    @property
    def commands(self) -> List[BaseCommandHandler]:
        return [self._init_handler(handler) for handler in command_handlers]

    @property
    def callbacks(self) -> List[BaseCallbackHandler]:
        return [self._init_handler(handler) for handler in callback_handlers]

    @property
    def messages(self) -> List[BaseMessageHandler]:
        return [self._init_handler(handler) for handler in message_handlers]
