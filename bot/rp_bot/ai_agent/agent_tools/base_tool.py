from abc import ABC, abstractmethod
from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from ....models.handlers_input import Person, Context, Message
from ...prompt_manager import PromptManager


class BaseTool(ABC):
    name: str
    description: str

    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        db: AsyncIOMotorDatabase,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
    ):
        self.person = person
        self.context = context
        self.message = message
        self.db = db
        self.models_toolkit = models_toolkit
        self.prompt_manager = prompt_manager

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
