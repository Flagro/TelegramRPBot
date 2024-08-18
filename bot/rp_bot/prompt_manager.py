from typing import Optional, List, Tuple
from datetime import datetime

from .db import DB
from ..models.handlers_input import Context


def get_current_date_prompt() -> str:
    date_prompt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Today's date and time is: {date_prompt}. "


class PromptManager:
    def __init__(self, db: DB) -> None:
        self.db = db

    async def compose_user_input(
        self,
        message: str,
        image_description: Optional[str],
        voice_description: Optional[str],
    ) -> str:
        # TODO: also add user name and context details
        result = [message]
        if image_description:
            result.append(image_description)
        if voice_description:
            result.append(voice_description)
        return " ".join(result)

    async def compose_bot_output(self, response_message: str) -> str:
        return response_message

    async def _compose_chat_mode_prompt(self, context: Context) -> str:
        chat_mode = await self.db.chat_modes.get_chat_mode(context)
        return f"The current chat mode is: {chat_mode.mode_name}. {chat_mode.mode_description}"

    async def compose_prompt(
        self, user_input: str, history: List[Tuple[str, bool, str]]
    ) -> str:
        # TODO: also add the names and context details in history
        current_date_prompt = get_current_date_prompt()
        return (
            "The conversation so far:\n"
            + "\n".join([f"{name}: {message}" for name, _, message in history])
            + f"\n\n{current_date_prompt}"
            + f"\n\nAnd the user just asked: {user_input}"
        )

    async def get_reply_system_prompt(self) -> str:
        return "You are a helpful assistant. Please provide a response to the user's query."
