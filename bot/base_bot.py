from abc import ABC, abstractmethod


class BaseBot(ABC):
    commands = []
    messages = []
    callbacks = []
