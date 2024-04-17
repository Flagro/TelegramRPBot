from telegram.ext import filters

import logging
from collections import namedtuple
from typing import List, Optional

from .handler_decorators import (
    command_handler,
    callback_handler,
    message_handler,
)
from .db import DB
from .ai import AI
from .localizer import Localizer
from .auth import authorized
from .keyboards import get_chat_modes_keyboard


CommandResponse = namedtuple("CommandResponse", ["text", "kwargs", "markup"])
MessageResponse = namedtuple("MessageResponse", ["text", "image_url"])


class RPBot:
    def __init__(
        self,
        db: DB,
        ai: AI,
    ):
        self.db = db
        self.ai = ai
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

        # Define bot commands
        Command = namedtuple("Command", ["command", "description_tag", "handler"])
        self.commands = [
            Command("reset", "reset_description", self._reset),
            Command("mode", "mode_description", self._mode),
            Command("addmode", "addmode_description", self._addmode),
            Command("deletemode", "deletemode_description", self._deletemode),
            Command("introduce", "introduce_description", self._introduce),
            Command("fact", "fact_description", self._fact),
            Command("clearfacts", "clearfacts_description", self._clearfacts),
            Command("usage", "usage_description", self._usage),
            Command("language", "language_description", self._language),
            Command("help", "help_description", self._help),
        ]
        Handler = namedtuple("Handler", ["filters", "handler"])
        self.handlers = [
            Handler(
                (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND,
                self._get_reply,
            ),
        ]
        Callback = namedtuple("Callbacks", ["pattern", "callback"])
        self.callbacks = [
            Callback("^show_chat_modes", self._show_chat_modes),
            Callback("^set_chat_mode", self._set_chat_mode),
            Callback("^delete_chat_mode", self._delete_chat_mode),
        ]
