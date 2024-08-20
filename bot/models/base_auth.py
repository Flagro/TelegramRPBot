from abc import ABC, abstractmethod

from .handlers_input import Person, Context


class BasePermission(ABC):
    @abstractmethod
    async def check(self, person: Person, context: Context) -> bool:
        raise NotImplementedError(
            "Permission check method must be implemented by subclasses."
        )
