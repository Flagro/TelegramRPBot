from abc import ABC, abstractmethod
from ..models.handlers_input import Person, Context
from ..models.handlers_response import CommandResponse


class Auth():
    def __init__(self, allowed_handles, admin_handles):
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles

    def is_allowed(self, user_handle):
        return user_handle in self.allowed_handles

    def is_admin(self, user_handle):
        return user_handle in self.admin_handles


class BasePermission(ABC):
    def __init__(self, func):
        self.func = func

    def __call__(self, person: Person, context: Context, auth: Auth):
        if self.check(person, context):
            return self.func(person, context)
        else:
            return CommandResponse("You do not have permission to use this command.")

    @abstractmethod
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        raise NotImplementedError("Permission check method must be implemented by subclasses.")


class GroupOwner(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        # Implement logic to check if the user is the group owner
        return True  # Placeholder


class GroupAdmin(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        # Implement logic to check if the user is an admin in the group
        return True  # Placeholder


class AllowedUser(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.allowed_users


class BotAdmin(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.bot_admins


class AnyUser(BasePermission):
    def check(self, person: Person, context: Context, auth: Auth) -> bool:
        return True  # Any user can use the command
