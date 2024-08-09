from typing import List
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


class RPBot(BaseBot):
    callbacks = callback_handlers
    commands = command_handlers
    messages = message_handlers

    def __init__(
        self,
        db_uri,
        openai_api_key,
        translations,
        default_chat_modes,
        ai_config,
        bot_config,
        allowed_handles,
        admin_handles,
        logger,
    ):
        # TODO: init here the handlers with parameters
        # and store them in a class attribute
        db = DB(
            db_uri=db_uri,
            default_language=bot_config.default_language,
            default_chat_modes=default_chat_modes,
            last_n_messages_to_remember=bot_config.last_n_messages_to_remember,
            default_usage_limit=bot_config.default_usage_limit,
        )

        ai = AI(openai_api_key=openai_api_key, db=db, ai_config=ai_config)

        localizer = Localizer(
            translations=translations, default_language=bot_config.default_language
        )

        auth = Auth(
            allowed_handles=allowed_handles,
            admin_handles=admin_handles,
            db=db,
        )
        self.ai = ai
        self.db = db
        self.localizer = localizer
        self.auth = auth  # TODO: init permissions
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

    def get_commands(self) -> List[BaseCommandHandler]:
        return [self._init_handler(handler) for handler in self.commands]

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        return [self._init_handler(handler) for handler in self.callbacks]

    def get_messages(self) -> List[BaseMessageHandler]:
        return [self._init_handler(handler) for handler in self.messages]
