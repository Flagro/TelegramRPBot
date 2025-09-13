import io
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    user_handle: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Context(BaseModel):
    chat_id: int
    chat_name: Optional[str] = None
    thread_id: Optional[int] = None
    is_group: bool = True
    is_bot_mentioned: bool = False
    is_group_admin: bool = False
    replied_to_user_handle: Optional[str] = None


class Message(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    message_text: str
    timestamp: datetime
    in_file_image: Optional[io.BytesIO] = None
    in_file_audio: Optional[io.BytesIO] = None


class BotInput(BaseModel):
    person: Person
    context: Context
    message: Message
    args: Optional[List[str]] = None


class TranscribedMessage(BaseModel):
    message_text: Optional[str] = None
    timestamp: datetime
    image_description: Optional[str] = None
    voice_description: Optional[str] = None
