from typing import Optional, Any

class CommandResponse:
    def __init__(self, text, kwargs: Optional[dict] = None, markup: Optional[Any] = None):
        self.text = text
        self.kwargs = kwargs
        self.markup = markup
        

class MessageResponse:
    def __init__(self, text, image_url: Optional[str] = None):
        self.text = text
        self.image_url = image_url
