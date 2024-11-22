from ....models.handlers_input import Person, Context, Message


class BaseTool:
    def __init__(self, person: Person, context: Context, message: Message):
        self.person = person
        self.context = context
        self.message = message
