from telegram import Update
from telegram.ext import CallbackContext

class BasePermission:
    def __init__(self, func):
        self.func = func

    def __call__(self, update: Update, context: CallbackContext):
        if self.check(update, context):
            return self.func(update, context)
        else:
            update.message.reply_text("You do not have permission to use this command.")

    def check(self, update: Update, context: CallbackContext) -> bool:
        raise NotImplementedError("Permission check method must be implemented by subclasses.")


class GroupOwner(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        # Implement logic to check if the user is the group owner
        return True  # Placeholder


class GroupAdmin(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        # Implement logic to check if the user is an admin in the group
        return True  # Placeholder


class AllowedUser(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.allowed_users


class BotAdmin(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.bot_admins


class AnyUser(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        return True  # Any user can use the command


class Auth():
    def __init__(self, allowed_handles, admin_handles):
        self.allowed_handles = allowed_handles
        self.admin_handles = admin_handles

    def is_allowed(self, user_handle):
        return user_handle in self.allowed_handles

    def is_admin(self, user_handle):
        return user_handle in self.admin_handles
