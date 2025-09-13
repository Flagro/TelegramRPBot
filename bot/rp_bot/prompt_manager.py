from datetime import datetime

from .db import DB
from ..models.handlers_input import Person, Context, TranscribedMessage


def _get_current_date_prompt() -> str:
    date_prompt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return date_prompt


class PromptManager:
    def __init__(self, db: DB) -> None:
        self.db = db

    async def _compose_user_input_prompt(
        self,
        person: Person,
        context: Context,
        transcribed_message: TranscribedMessage,
    ) -> str:
        # TODO: also add user name and context details
        result = [transcribed_message.message_text]
        if transcribed_message.image_description:
            image_prompt = (
                "The text description of the image is: "
                f"{transcribed_message.image_description}"
            )
            result.append(image_prompt)
        if transcribed_message.voice_description:
            voice_prompt = (
                "The text description of the attached voice audio is: "
                f"{transcribed_message.voice_description}"
            )
            result.append(voice_prompt)
        message_prompt = " ".join(result)
        return f"The user {person.user_handle} just said: {message_prompt}"

    async def compose_engage_needed_prompt(self, user_input: str) -> str:
        return (
            "Your task is to determine wether or not we can somehow "
            "engage after the user's input. "
            "Note that engagement is expensive and should be used only when necessary like "
            "explicit question for a bot or a request for general knowledge or when user is actively "
            "engaged in the conversation with the bot."
            f"The user just said: {user_input}"
        )

    async def _compose_chat_mode_prompt(self, context: Context) -> str:
        chat_mode = await self.db.chat_modes.get_chat_mode(context)
        return f"The current chat mode is: {chat_mode.mode_name}. {chat_mode.mode_description}"

    async def compose_chat_facts_prompt(self, context: Context) -> str:
        # TODO: this should be an optional tool
        chat_facts = await self.db.user_facts.get_chat_facts(context)
        return (
            "The following facts are known about the users in this chat:\n"
            + "\n".join([f"{user}: {fact}" for user, fact in chat_facts])
        )

    async def compose_user_facts_prompt(self, person: Person, context: Context) -> str:
        user_facts = await self.db.user_facts.get_user_facts(context, person)
        return "The following facts are known about you:\n" + "\n".join(user_facts)

    async def _compose_user_introduction_prompt(
        self, person: Person, context: Context
    ) -> str:
        user_introduction = await self.db.user_introductions.get_user_introduction(
            context, person
        )
        return f"Introduction of a user who requested the response: {user_introduction}"

    async def _compose_chat_history_prompt(self, user_input, context: Context) -> str:
        messages_history = await self.db.dialogs.get_messages(context)
        if len(messages_history) <= 1:
            return "It's the first message in the chat.\n"
        # Take everything besides the last one since the last one is the current message
        messages_history_prompt = "\n".join(
            [f"{name}: {message}" for name, _, message in messages_history[:-1]]
        )
        return "The conversation so far:\n" f"{messages_history_prompt}\n\n"

    async def compose_prompt(
        self,
        initiator: Person,
        context: Context,
        user_transcribed_message: TranscribedMessage,
    ) -> str:
        current_date = _get_current_date_prompt()
        current_date_prompt = f"Today's date and time is: {current_date}"
        user_input_prompt = await self._compose_user_input_prompt(
            person=initiator,
            context=context,
            transcribed_message=user_transcribed_message,
        )
        chat_history_prompt = await self._compose_chat_history_prompt(
            user_input_prompt, context
        )
        chat_facts_prompt = await self.compose_chat_facts_prompt(context)
        user_facts_prompt = await self.compose_user_facts_prompt(initiator, context)
        user_introduction_prompt = await self._compose_user_introduction_prompt(
            initiator, context
        )
        return "\n".join(
            [
                current_date_prompt,
                user_input_prompt,
                chat_history_prompt,
                chat_facts_prompt,
                user_facts_prompt,
                user_introduction_prompt,
            ]
        )

    async def get_reply_system_prompt(self, context: Context) -> str:
        chat_name = context.chat_name
        chat_mode_prompt = await self._compose_chat_mode_prompt(context)
        chat_language = await self.db.chats.get_language(context)
        return (
            "You are a helpful assistant. "
            f"You are currently in the chat: {chat_name}. "
            f"{chat_mode_prompt} "
            "Please provide a response to the user's query. "
            f"The chat that is used in chat is: {chat_language} "
            "but do not hesitate to answer in another language if user's query is in another language. "
        )
