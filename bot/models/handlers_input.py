import io
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    user_handle: str
    first_name: str
    last_name: str


class Context(BaseModel):
    chat_id: int
    chat_name: str
    thread_id: Optional[int] = None
    is_group: bool = True
    is_bot_mentioned: bool = False
    is_group_admin: bool = False
    replied_to_user_handle: Optional[str] = None


class Message(BaseModel):
    message_text: str
    timestamp: datetime
    in_file_image: Optional[io.BytesIO] = None
    in_file_audio: Optional[io.BytesIO] = None


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
