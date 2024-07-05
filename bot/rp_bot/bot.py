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


class RPBot(BaseBot):
    callbacks = callback_handlers
    commands = command_handlers
    messages = message_handlers

    def _init_handler(self, handler):
        return handler(
            db=self.db,
            ai=self.ai,
            localizer=self.localizer,
            auth=self.auth,
        )

    def get_commands(self) -> List[BaseCommandHandler]:
        return [self._init_handler(handler) for handler in self.commands]

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        return [self._init_handler(handler) for handler in self.callbacks]

    def get_messages(self) -> List[BaseMessageHandler]:
        return [self._init_handler(handler) for handler in self.messages]

    def __init__(self, ai, db, localizer, auth, bot_config, logger):
        # TODO: init here the handlers with parameters
        # and store them in a class attribute
        self.ai = ai
        self.db = db
        self.localizer = localizer
        self.auth = auth  # TODO: init permissions
        self.logger = logger
