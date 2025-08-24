from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from .agent_toolkit import AIAgentToolkit
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message


class AIAgent:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        db: AsyncIOMotorDatabase,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
    ):
        self.toolkit = AIAgentToolkit(
            person, context, message, db, models_toolkit, prompt_manager
        )
