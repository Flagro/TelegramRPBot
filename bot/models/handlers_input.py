from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    user_handle: str
    first_name: str
    last_name: str
    is_group_admin: bool


class Context(BaseModel):
    chat_id: int
    chat_name: str
    thread_id: Optional[int]
    is_group: bool
    is_bot_mentioned: bool
    replied_to_user_handle: Optional[str] = None


class Message(BaseModel):
    message_text: str
    timestamp: datetime
    in_file_image: Optional[str] = None
    in_file_audio: Optional[str] = None


class BotInput(BaseModel):
    person: Person
    context: Context
    message: Message
    args: Optional[str] = None


class TranscribedMessage(BaseModel):
    message_text: str
    timestamp: datetime
    image_description: Optional[str] = None
    voice_description: Optional[str] = None
