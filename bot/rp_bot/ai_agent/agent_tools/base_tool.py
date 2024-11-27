from abc import ABC, abstractmethod
from ....models.handlers_input import Person, Context, Message


class BaseTool(ABC):
    name: str
    description: str

    def __init__(self, person: Person, context: Context, message: Message):
        self.person = person
        self.context = context
        self.message = message

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass
