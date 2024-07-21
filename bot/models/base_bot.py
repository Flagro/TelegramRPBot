from .base_handlers import BaseCommandHandler, BaseMessageHandler, BaseCallbackHandler
from abc import ABC, abstractmethod
from typing import List


class BaseBot(ABC):
    @abstractmethod
    def get_commands(self) -> List[BaseCommandHandler]:
        raise NotImplementedError

    @abstractmethod
    def get_callbacks(self) -> List[BaseCallbackHandler]:
        raise NotImplementedError

    @abstractmethod
    def get_messages(self) -> List[BaseMessageHandler]:
        raise NotImplementedError
