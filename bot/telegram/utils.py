from __future__ import annotations

import io
import asyncio

from typing import List, Optional

from telegram import Update
from telegram.ext import ContextTypes

from ..models.handlers_input import Person, Context, Message


def is_callback(update: Update) -> bool:
    return update.callback_query is not None


def get_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Context:
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


def get_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Person:
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


def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
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


def get_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    if is_callback(update):
        query = update.callback_query
        asyncio.run(query.answer)
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
    return not (is_private_chat or bot_in_reply_tree or is_bot_mentioned)


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
