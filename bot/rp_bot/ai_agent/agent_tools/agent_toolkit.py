from .autofact_generation import CheckIfFactsNeededTool, ComposeFactsBasedOnMessagesTool
from .check_engage_needed import CheckEngageNeededTool
from .generate_image import ImageGeneratorTool
from .get_facts import GetChatFactsTool, GetUserFactsTool
from .get_response import GetResponseTool
from ..models_toolkit import ModelsToolkit
from ...prompt_manager import PromptManager
from ....models.handlers_input import Person, Context, Message


class AIAgentToolkit:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        models_toolkit: ModelsToolkit,
        prompt_manager: PromptManager,
    ):
        self.check_if_facts_needed = CheckIfFactsNeededTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.compose_facts_based_on_messages = ComposeFactsBasedOnMessagesTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.check_engage_needed = CheckEngageNeededTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.image_generator = ImageGeneratorTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.get_chat_facts = GetChatFactsTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.get_user_facts = GetUserFactsTool(
            person, context, message, models_toolkit, prompt_manager
        )
        self.get_response = GetResponseTool(
            person, context, message, models_toolkit, prompt_manager
        )
