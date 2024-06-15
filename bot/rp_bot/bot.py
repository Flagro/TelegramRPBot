from typing import List
from bot.models.base_handlers import BaseCallbackHandler, BaseCommandHandler, BaseMessageHandler
from ..models.base_bot import BaseBot
from .commands import handlers as command_handlers
from .callbacks import handlers as callback_handlers
from .messages import handlers as message_handlers


class RPBot(BaseBot):
    callbacks = callback_handlers
    commands = command_handlers
    messages = message_handlers

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        return self.callbacks

    def get_commands(self) -> List[BaseCommandHandler]:
        return self.commands

    def get_messages(self) -> List[BaseMessageHandler]:
        return self.messages

    def __init__(self, ai, db, localizer, auth, logger):
        # TODO: init here the handlers with parameters
        # and store them in a class attribute
        for handler in self.callbacks + self.commands + self.messages:
            handler.ai = ai
            handler.db = db
            handler.localizer = localizer
            handler.auth = auth  # TODO: init permissions
            handler.logger = logger
