from abc import ABC, abstractmethod
import logging

from ..rp_bot.db import DB
from ..rp_bot.ai import AI
from ..rp_bot.localizer import Localizer


class BaseHandler(ABC):
    def __init__(self, db: DB, ai: AI, localizer: Localizer):
        self.db = db
        self.ai = ai
        self.localizer = localizer
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")
        
    @abstractmethod
    def handle(self):
        raise NotImplementedError


class BaseCallbackHandler(BaseHandler, ABC):
    pattern = None

    @abstractmethod
    def handle(self, Person, Context, args):
        self.db.create_user_if_not_exists(Person)
        context_response = self.get_callback_response(Person, Context, args)
        response = self.localizer.get_command_response(context_response.tag, context_response.kwargs)
        return response

    @abstractmethod
    def get_callback_response(self, tag, kwargs=None):
        raise NotImplementedError


class BaseMessageHandler(BaseHandler, ABC):
    filters = None

    def handle(self, Person, Context, args):
        self.db.create_user_if_not_exists(Person)
        context_response = self.get_command_response(Person, Context, args)
        response = self.localizer.get_command_response(context_response.tag, context_response.kwargs)
        return response

    @abstractmethod    
    def get_command_response(self, tag, kwargs=None):
        raise NotImplementedError


class BaseCommandHandler(BaseHandler, ABC):
    command = None
    description_tag = None

    def handle(self, Person, Context, args):
        self.db.create_user_if_not_exists(Person)
        return self.get_reply(Person, Context, args)

    @abstractmethod
    def get_reply(self, Person, Context, args):
        raise NotImplementedError
