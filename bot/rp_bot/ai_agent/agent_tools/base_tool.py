from abc import ABC, abstractmethod

from ....models.handlers_input import Person, Context, Message
from ..models_toolkit import ModelsToolkit


class BaseTool(ABC):
    name: str
    description: str

    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        models_toolkit: ModelsToolkit,
    ):
        self.person = person
        self.context = context
        self.message = message
        self.models_toolkit = models_toolkit

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
