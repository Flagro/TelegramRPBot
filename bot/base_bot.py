from abc import ABC, abstractmethod


class BaseBot(ABC):
    @abstractmethod
    def get_commands(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_callbacks(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_messages(self):
        raise NotImplementedError
