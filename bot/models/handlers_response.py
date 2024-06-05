from typing import Optional, Dict
from uuid import UUID


class CommandResponse:
    def __init__(self, text, kwargs: Optional[dict] = None):
        self.text = text
        self.kwargs = kwargs


class KeyboardResponse:
    def __init__(
        self,
        text,
        kwargs: Optional[dict],
        modes_dict: Dict[UUID, str],
        callback: str,
        button_action: str,
    ):
        self.text = text
        self.kwargs = kwargs
        self.modes_dict = modes_dict
        self.callback = callback
        self.button_action = button_action
