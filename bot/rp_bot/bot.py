from typing import List
from bot.models.base_handlers import BaseCallbackHandler
from ..models.base_bot import BaseBot
from .commands import handlers as command_handlers
from .callbacks import handlers as callback_handlers
from .messages import handlers as message_handlers


class RPBot(BaseBot):
    def __init__(self, ai, db, localizer, auth, logger):
        # TODO: init here the handlers with parameters
        # and store them in a class attribute
        pass

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        return callback_handlers
    
    def get_commands(self) -> List[BaseCallbackHandler]:
        return command_handlers

    def get_messages(self) -> List[BaseCallbackHandler]:
        return message_handlers
