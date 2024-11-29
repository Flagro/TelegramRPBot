from .describe_image import DescribeImageUtililty
from ..models_toolkit import ModelsToolkit

from ....models.handlers_input import Person, Context, Message


class AgentUtils:
    def __init__(
        self,
        person: Person,
        context: Context,
        message: Message,
        models_toolkit: ModelsToolkit,
    ):
        self.describe_image = DescribeImageUtililty(
            person, context, message, models_toolkit
        )
