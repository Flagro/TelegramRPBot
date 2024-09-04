from typing import List, Union, Type
from logging import Logger
from ..models.base_bot import BaseBot
from .rp_bot_handlers import (
    RPBotCommandHandler,
    RPBotCallbackHandler,
    RPBotMessageHandler,
)
from .commands import handlers as command_handlers
from .callbacks import handlers as callback_handlers
from .messages import handlers as message_handlers
from .ai_agent.ai import AI
from .db import DB
from .auth import Auth
from .prompt_manager import PromptManager
from .localizer import Localizer
from ..models.config import (
    BotConfig,
    DefaultChatModes,
    LocalizerTranslations,
    AIConfig,
)


def get_rp_bot(
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
    db = DB(
        db_uri=db_uri,
        default_language=bot_config.default_language,
        default_chat_modes=default_chat_modes,
        last_n_messages_to_remember=bot_config.last_n_messages_to_remember,
        last_n_messages_to_store=bot_config.last_n_messages_to_store,
        default_usage_limit=bot_config.default_usage_limit,
    )
    ai = AI(openai_api_key=openai_api_key, ai_config=ai_config)
    localizer = Localizer(
        db=db,
        translations=translations,
        default_language=bot_config.default_language,
    )
    prompt_manager = PromptManager(db=db)
    auth = Auth(
        allowed_handles=allowed_handles,
        admin_handles=admin_handles,
        db=db,
    )
    return RPBot(
        db=db,
        ai=ai,
        localizer=localizer,
        prompt_manager=prompt_manager,
        auth=auth,
        bot_config=bot_config,
        logger=logger,
    )


class RPBot(BaseBot):
    def __init__(
        self,
        db: DB,
        ai: AI,
        localizer: Localizer,
        prompt_manager: PromptManager,
        auth: Auth,
        bot_config: BotConfig,
        logger: Logger,
    ):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.prompt_manager = prompt_manager
        self.auth = auth
        self.bot_config = bot_config
        self.logger = logger

    def _init_handler(
        self,
        handler: Union[
            Type[RPBotCommandHandler],
            Type[RPBotCallbackHandler],
            Type[RPBotMessageHandler],
        ],
    ) -> Union[RPBotCommandHandler, RPBotCallbackHandler, RPBotMessageHandler]:
        return handler(
            db=self.db,
            ai=self.ai,
            localizer=self.localizer,
            prompt_manager=self.prompt_manager,
            auth=self.auth,
            bot_config=self.bot_config,
            logger=self.logger.getChild(handler.__name__),
        )

    @property
    def commands(self) -> List[RPBotCommandHandler]:
        return [self._init_handler(handler) for handler in command_handlers]

    @property
    def callbacks(self) -> List[RPBotCallbackHandler]:
        return [self._init_handler(handler) for handler in callback_handlers]

    @property
    def messages(self) -> List[RPBotMessageHandler]:
        return [self._init_handler(handler) for handler in message_handlers]
