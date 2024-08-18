from typing import Optional, List, Tuple
from datetime import datetime

from .db import DB
from ..models.handlers_input import Context, TranscribedMessage


def get_current_date_prompt() -> str:
    date_prompt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Today's date and time is: {date_prompt}. "


class PromptManager:
    def __init__(self, db: DB) -> None:
        self.db = db

    async def _compose_user_input_prompt(
        self,
        transcribed_message: TranscribedMessage,
    ) -> str:
        # TODO: also add user name and context details
        result = [transcribed_message.message_text]
        if transcribed_message.image_description:
            result.append(transcribed_message.image_description)
        if transcribed_message.voice_description:
            result.append(transcribed_message.voice_description)
        return " ".join(result)

    async def _compose_chat_mode_prompt(self, context: Context) -> str:
        chat_mode = await self.db.chat_modes.get_chat_mode(context)
        return f"The current chat mode is: {chat_mode.mode_name}. {chat_mode.mode_description}"

    async def _compose_chat_history_prompt(self, user_input, context: Context) -> str:
        # TODO: also add the names and context details in history

        # Take everything besides the last one since the last one is the current message
        messages_history = (await self.db.dialogs.get_messages(context))[0:-1]
        return (
            "The conversation so far:\n"
            + "\n".join([f"{name}: {message}" for name, _, message in messages_history])
            + f"\n\nAnd the user just asked: {user_input}"
        )

    async def compose_prompt(
        self, user_transcribed_message: TranscribedMessage, context: Context
    ) -> str:
        current_date_prompt = get_current_date_prompt()
        chat_mode_prompt = await self._compose_chat_mode_prompt(context)
        user_input_prompt = await self._compose_user_input_prompt(
            transcribed_message=user_transcribed_message
        )
        chat_history_prompt = await self._compose_chat_history_prompt(
            user_input_prompt, context
        )
        return f"{current_date_prompt} {chat_mode_prompt} {chat_history_prompt}"

    async def get_reply_system_prompt(self) -> str:
        return "You are a helpful assistant. Please provide a response to the user's query."
