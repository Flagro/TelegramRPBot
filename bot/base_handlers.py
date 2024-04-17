from abc import ABC, abstractmethod


class CallbackHandler(ABC):
    def __init__(self, db, ai, localizer):
        self.db = db
        self.ai = ai
        self.localizer = localizer

    def handle(self, update, context):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text="Selected option: {}".format(query.data))
        return self.bot.STATES.END
