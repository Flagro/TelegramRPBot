from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.handlers_input import Person, Context
from .db import DB


class Auth:
    def __init__(
        self,
        allowed_handles: Optional[List[str]],
        admin_handles: Optional[List[str]],
        db: DB,
    ):
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles
        self.db = db

    async def is_allowed(self, user_handle):
        return self.allowed_handles is None or user_handle in self.allowed_handles

    async def is_admin(self, user_handle):
        return self.admin_handles is not None and user_handle in self.admin_handles

    async def is_banned(self, user_handle):
        return await self.db.users.is_user_banned(user_handle)


class BasePermission(ABC):
    @abstractmethod
    async def check(self, person: Person, context: Context, auth: Auth) -> bool:
        raise NotImplementedError(
            "Permission check method must be implemented by subclasses."
        )


class GroupAdmin(BasePermission):
    async def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return person.is_group_admin


class AllowedUser(BasePermission):
    async def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return await auth.is_allowed(person.user_handle)


class BotAdmin(BasePermission):
    async def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return await auth.is_admin(person.user_handle)


class NotBanned(BasePermission):
    async def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return not await auth.is_banned(person.user_handle)
