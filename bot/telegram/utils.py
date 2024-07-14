from __future__ import annotations

import io

from typing import List, Optional, AsyncIterator

from telegram import Update, constants
from telegram.ext import ContextTypes

from ..models.handlers_input import Person, Context, Message
from ..models.handlers_response import LocalizedCommandResponse


def is_callback(update: Update) -> bool:
    return update.callback_query is not None


async def get_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Context:
    if is_callback(update):
        return Context(
            chat_id=update.callback_query.message.chat.id,
            thread_id=None,
            is_group=True,
            is_bot_mentioned=False,
        )
    else:
        return Context(
            chat_id=update.message.chat_id,
            thread_id=get_thread_id(update),
            is_group=True,
            is_bot_mentioned=bot_mentioned(update, context),
        )


async def get_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Person:
    if is_callback(update):
        return Person(
            user_id=update.callback_query.from_user.id,
            user_handle="@" + update.callback_query.from_user.username,
            first_name=update.callback_query.from_user.first_name,
            last_name=update.callback_query.from_user.last_name,
            is_group_admin=False,  # TODO: check this properly
            is_group_owner=False,  # TODO: check this properly
        )
    else:
        return Person(
            user_id=update.message.from_user.id,
            user_handle="@" + update.message.from_user.username,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            is_group_admin=False,  # TODO: check this properly
            is_group_owner=False,  # TODO: check this properly
        )


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    if is_callback(update):
        return Message(
            message_text=update.callback_query.message.text,
            in_file_image=None,
            in_file_audio=None,
        )
    message = update.message.text
    is_bot_mentioned = bot_mentioned(update, context)
    # get image and audio in memory
    image = None
    if is_bot_mentioned and update.message.photo:
        image = get_file_in_memory(update.message.photo[-1].file_id, context)

    voice = None
    if is_bot_mentioned and update.message.voice:
        voice = get_file_in_memory(update.message.voice.file_id, context)
    return Message(
        message_text=message,
        in_file_image=image,
        in_file_audio=voice,
    )


async def get_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    if is_callback(update):
        query = update.callback_query
        await query.answer()
        args = query.data.split("|")[1:]
        return args
    else:
        return context.args


def bot_mentioned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    is_private_chat = update.message.chat.type == "private"
    is_bot_mentioned = (
        update.message.text is not None
        and ("@" + context.bot.username) in update.message.text
    )
    bot_in_reply_tree = (
        update.message.reply_to_message is not None
        and update.message.reply_to_message.from_user.id == context.bot.id
    )
    return is_private_chat or bot_in_reply_tree or is_bot_mentioned


async def get_file_in_memory(
    file_id: str, context: ContextTypes.DEFAULT_TYPE
) -> io.BytesIO:
    file = await context.bot.getFile(file_id)
    file_stream = io.BytesIO()
    await file.download(out=file_stream)
    file_stream.seek(0)
    return file_stream


def get_thread_id(update: Update) -> Optional[str]:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def min_char_diff_for_buffering(content: str, is_group_chat: bool) -> int:
    """
    Get the minimum string length difference to trigger new yield in the streaming response
    """
    if is_group_chat:
        return (
            180
            if len(content) > 1000
            else 120 if len(content) > 200 else 90 if len(content) > 50 else 50
        )
    return (
        90
        if len(content) > 1000
        else 45 if len(content) > 200 else 25 if len(content) > 50 else 15
    )


def is_group_chat(update: Update) -> bool:
    if not update.effective_chat:
        return False
    return update.effective_chat.type in [
        constants.ChatType.GROUP,
        constants.ChatType.SUPERGROUP,
    ]


async def buffer_streaming_response(
    stream: AsyncIterator[LocalizedCommandResponse], is_group_chat: bool
) -> AsyncIterator[LocalizedCommandResponse]:
    last_response_len = 0
    current_response = None
    i = 0
    async for chunk in stream:
        current_response = chunk
        i += 1
        if len(chunk.localized_text) - last_response_len > min_char_diff_for_buffering(
            chunk.localized_text, is_group_chat
        ):
            yield current_response
            current_response = None
            i = 0
            last_response_len = len(chunk.localized_text)
    if i:
        yield current_response
