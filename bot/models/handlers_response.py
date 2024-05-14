from typing import Optional, Any
from uuid import UUID


class CommandResponse:
    def __init__(self, text, kwargs: Optional[dict] = None):
        self.text = text
        self.kwargs = kwargs


class MessageResponse:
    def __init__(self, text, image_url: Optional[str] = None):
        self.text = text
        self.image_url = image_url


class ListResponse:
    def __init__(
        self,
        text,
        kwargs: Optional[dict],
        names: list[str],
        ids: list[UUID],
        callback: str,
        button_action: str,
    ):
        self.text = text
        self.kwargs = kwargs
        self.names = names
        self.ids = ids
        self.callback = callback
        self.button_action = button_action
