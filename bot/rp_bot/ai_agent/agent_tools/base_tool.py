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

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    async def arun(self, *args, **kwargs):
        raise NotImplementedError

    async def get_response(self, question: str) -> bool:
        llm = self.models_toolkit.llm
        response = await llm.chat.completions.create(
            model=self.models_toolkit._get_default_model("text").name,
            messages=[
                {"role": "system", "content": question},
            ],
            stream=False,
            temperature=self.models_toolkit.ai_config.TextGeneration.temperature,
        )
        text_response = response.choices[0].message.content
        return text_response

    async def ask_yes_no_question(self, question: str) -> bool:
        text_response = await self.get_response(question)
        lower_response = text_response.lower()
        if "yes" in lower_response:
            return True
        if "no" in lower_response:
            return False
        return False
