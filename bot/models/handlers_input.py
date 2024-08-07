from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Person(BaseModel):
    user_id: int
    user_handle: str
    first_name: str
    last_name: str
    is_group_admin: bool


class Context(BaseModel):
    chat_id: int
    thread_id: Optional[int]
    is_group: bool
    is_bot_mentioned: bool
    replied_to_user_handle: Optional[str] = None


class Message(BaseModel):
    message_text: str
    timestamp: datetime
    in_file_image: Optional[str] = None
    in_file_audio: Optional[str] = None
