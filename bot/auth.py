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
