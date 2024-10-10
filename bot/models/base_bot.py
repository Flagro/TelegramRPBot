from abc import ABC, abstractmethod
from typing import List

from .base_handlers import BaseCommandHandler, BaseMessageHandler, BaseCallbackHandler


class BaseBot(ABC):
    @property
    @abstractmethod
    def commands(self) -> List[BaseCommandHandler]:
        raise NotImplementedError

    @property
    @abstractmethod
    def callbacks(self) -> List[BaseCallbackHandler]:
        raise NotImplementedError

    @property
    @abstractmethod
    def messages(self) -> List[BaseMessageHandler]:
        raise NotImplementedError
