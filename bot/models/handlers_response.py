from typing import Optional, Dict
from uuid import UUID


class KeyboardResponse:
    def __init__(
        self,
        modes_dict: Dict[UUID, str],
        callback: str,
        button_action: str,
    ):
        self.modes_dict = modes_dict
        self.callback = callback
        self.button_action = button_action


class CommandResponse:
    def __init__(self, text, kwargs: Optional[dict] = None, keyboard: Optional[KeyboardResponse] = None):
        self.text = text
        self.kwargs = kwargs
        self.keyboard = keyboard
