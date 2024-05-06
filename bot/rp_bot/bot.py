from typing import List
from bot.models.base_handlers import BaseCallbackHandler
from ..models.base_bot import BaseBot


class RPBot(BaseBot):
    def __init__(self, ai, db, localizer, auth, logger):
        pass

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        return super().get_callbacks()
    
    def get_commands(self) -> List[BaseCallbackHandler]:
        return super().get_commands()

    def get_messages(self) -> List[BaseCallbackHandler]:
        return super().get_messages()
