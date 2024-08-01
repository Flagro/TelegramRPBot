from typing import Optional, Dict
from collections import OrderedDict
from uuid import UUID
from pydantic import BaseModel


class KeyboardResponse(BaseModel):
    modes_dict: OrderedDict[UUID, str]
    callback: str
    button_action: str


class CommandResponse(BaseModel):
    text: str
    kwargs: Optional[Dict] = None
    keyboard: Optional[KeyboardResponse] = None


class LocalizedCommandResponse(BaseModel):
    localized_text: str
    keyboard: Optional[KeyboardResponse] = None
