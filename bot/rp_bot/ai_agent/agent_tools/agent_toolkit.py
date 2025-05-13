from omnimodkit import ModelsToolkit
from motor.motor_asyncio import AsyncIOMotorDatabase
from .autofact_generation import CheckIfFactsNeededTool, ComposeFactsBasedOnMessagesTool
from .check_engage_needed import CheckEngageNeededTool
from .get_facts import GetChatFactsTool, GetUserFactsTool
from .get_response import GetResponseTool
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
        self.check_if_facts_needed = CheckIfFactsNeededTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.compose_facts_based_on_messages = ComposeFactsBasedOnMessagesTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.check_engage_needed = CheckEngageNeededTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.get_chat_facts = GetChatFactsTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.get_user_facts = GetUserFactsTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
        self.get_response = GetResponseTool(
            person, context, message, db, models_toolkit, prompt_manager
        )
