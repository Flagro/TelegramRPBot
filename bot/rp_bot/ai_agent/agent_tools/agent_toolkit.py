from .autofact_generation import CheckIfFactsNeededTool, ComposeFactsBasedOnMessagesTool
from .check_engage_needed import CheckEngageNeededTool
from .generate_image import ImageGeneratorTool
from .get_facts import GetChatFactsTool, GetUserFactsTool
from .get_response import GetResponseTool

from ....models.handlers_input import Person, Context, Message


class AIAgentToolkit:
    def __init__(self, person: Person, context: Context, message: Message):
        self.check_if_facts_needed = CheckIfFactsNeededTool(person, context, message)
        self.compose_facts_based_on_messages = ComposeFactsBasedOnMessagesTool(
            person, context, message
        )
        self.check_engage_needed = CheckEngageNeededTool(person, context, message)
        self.image_generator = ImageGeneratorTool(person, context, message)
        self.get_chat_facts = GetChatFactsTool(person, context, message)
        self.get_user_facts = GetUserFactsTool(person, context, message)
        self.get_response = GetResponseTool(person, context, message)
