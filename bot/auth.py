from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps


def authorized(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_handle = "@" + update.message.from_user.username
        self.db.create_user_if_not_exists(user_handle)
        if user_handle not in self.allowed_handles:
            # TODO: log unauthorized access
            return
        return await func(self, update, context)

    return wrapper


from functools import wraps
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
    allowed_users = ['user_id1', 'user_id2']  # User IDs from config
    
    def check(self, update: Update, context: CallbackContext) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.allowed_users


class BotAdmin(BasePermission):
    bot_admins = ['admin_id1', 'admin_id2']  # Admin IDs from config
    
    def check(self, update: Update, context: CallbackContext) -> bool:
        user_id = update.effective_user.id
        return str(user_id) in self.bot_admins


class AnyUser(BasePermission):
    def check(self, update: Update, context: CallbackContext) -> bool:
        return True  # Any user can use the command
