from abc import ABC, abstractmethod
from functools import wraps
import logging

from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from ..rp_bot.localizer import Localizer
from ..rp_bot.auth import Auth
from ..models.handlers_input import Person, Context, Message


class BaseHandler(ABC):
    permissions: list = []
    
    def __init__(self, db: DB, ai: AI, localizer: Localizer, auth: Auth):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.auth = auth
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

    @abstractmethod
    def handle(self):
        raise NotImplementedError


def is_authenticated(func):
    @wraps(func)
    def wrapper(self, person: Person, context: Context, *args, **kwargs):
        for permission in self.permissions:
            if not permission(person, context, self.auth):
                return self.localizer.get_command_response("not_authenticated")
        self.db.create_user_if_not_exists(person)
        return func(self, person, context, *args, **kwargs)


class BaseCallbackHandler(BaseHandler, ABC):
    callback_action: str = None

    @is_authenticated
    def handle(self, person: Person, context: Context, args: list):
        callback_response = self.get_callback_response(person, context, args)
        response = self.localizer.get_command_response(
            callback_response.tag, callback_response.kwargs
        )
        return response

    @abstractmethod
    def get_callback_response(self, tag, kwargs=None):
        raise NotImplementedError


class BaseCommandHandler(BaseHandler, ABC):
    command = None

    @is_authenticated
    def handle(self, person: Person, context: Context, args):
        command_response = self.get_command_response(person, context, args)
        response = self.localizer.get_command_response(
            command_response.tag, command_response.kwargs
        )
        return response

    @abstractmethod
    def get_command_response(self, person: Person, context: Context, args):
        raise NotImplementedError


class BaseMessageHandler(BaseHandler, ABC):
    filters = None

    @is_authenticated
    def handle(self, person: Person, context: Context, message: Message):
        message_response = self.get_reply(person, context, message)
        return message_response

    @abstractmethod
    def get_reply(self, person: Person, message: Message):
        raise NotImplementedError
