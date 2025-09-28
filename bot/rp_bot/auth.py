from abc import ABC
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

    async def has_accepted_terms(self, user_handle):
        return await self.db.users.has_accepted_terms(user_handle)


class BaseRPBotPermission(ABC):
    def __init__(self, auth: Auth):
        self.auth = auth


class GroupAdmin(BaseRPBotPermission):
    async def check(self, person: Person, context: Context) -> bool:
        return context.is_group_admin


class AllowedUser(BaseRPBotPermission):
    async def check(self, person: Person, context: Context) -> bool:
        return await self.auth.is_allowed(person.user_handle)


class BotAdmin(BaseRPBotPermission):
    async def check(self, person: Person, context: Context) -> bool:
        return await self.auth.is_admin(person.user_handle)


class NotBanned(BaseRPBotPermission):
    async def check(self, person: Person, context: Context) -> bool:
        return not await self.auth.is_banned(person.user_handle)


class HasAcceptedTerms(BaseRPBotPermission):
    async def check(self, person: Person, context: Context) -> bool:
        return await self.auth.has_accepted_terms(person.user_handle)
