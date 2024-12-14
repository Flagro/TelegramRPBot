from abc import ABC, abstractmethod

from ....models.handlers_input import Person, Context, Message
from ..models_toolkit import ModelsToolkit
from ...prompt_manager import PromptManager


class BaseTool(ABC):
    name: str
    description: str

    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
    ):
        self.person = person
        self.context = context
        self.message = message
        self.models_toolkit = models_toolkit
        self.prompt_manager = prompt_manager

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
