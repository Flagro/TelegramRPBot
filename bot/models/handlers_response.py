from typing import Optional, Dict
from collections import OrderedDict
from pydantic import BaseModel, Field


class KeyboardResponse(BaseModel):
    modes_dict: OrderedDict[str, str]
    callback: str
    button_action: str


class CommandResponse(BaseModel):
    text: str
    kwargs: Dict = Field(default_factory=dict)
    keyboard: Optional[KeyboardResponse] = None


class LocalizedCommandResponse(BaseModel):
    localized_text: str
    keyboard: Optional[KeyboardResponse] = None
