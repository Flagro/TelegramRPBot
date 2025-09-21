from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message


class AIAgentToolkit:
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
