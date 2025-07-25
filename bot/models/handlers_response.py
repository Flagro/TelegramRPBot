import io
from typing import Optional, Dict
from collections import OrderedDict
from pydantic import BaseModel


class KeyboardResponse(BaseModel):
    modes_dict: OrderedDict[str, str]
    callback: str
    button_action: str


class CommandResponse(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None
    audio_bytes: Optional[io.BytesIO] = None
    kwargs: Optional[Dict[str, str]] = None
    keyboard: Optional[KeyboardResponse] = None


class LocalizedCommandResponse(BaseModel):
    localized_text: Optional[str] = None
    keyboard: Optional[KeyboardResponse] = None
