from abc import ABC, abstractmethod
from ..models.handlers_input import Person, Context


class Auth:
    def __init__(self, allowed_handles, admin_handles, db):
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles
        self.db = db

    def is_allowed(self, user_handle):
        return user_handle in self.allowed_handles

    def is_admin(self, user_handle):
        return user_handle in self.admin_handles

    def is_banned(self, user_handle):
        return self.db.users.is_user_banned(user_handle)


class BasePermission(ABC):
    def __call__(self, person: Person, context: Context, auth: Auth):
        if self.check(person, context, auth):
            return True
        else:
            return False

    @abstractmethod
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        raise NotImplementedError(
            "Permission check method must be implemented by subclasses."
        )


class GroupOwner(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return person.is_group_owner


class GroupAdmin(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return person.is_group_admin


class AllowedUser(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return auth.is_allowed(person.user_handle)


class BotAdmin(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return auth.is_admin(person.user_handle)


class NotBanned(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return not auth.is_banned(person.user_handle)
