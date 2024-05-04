from __future__ import annotations

import io
import asyncio
import logging

from typing import List

import telegram
from telegram import Update, constants
from telegram.ext import CallbackContext, ContextTypes

from ..models.handlers_input import Person, Context, Message


def get_context(update: Update, context) -> Context:
    if type(context) == ContextTypes.DEFAULT_TYPE:
        return Context(
            chat_id=update.message.chat_id,
            thread_id=get_thread_id(update),
            is_bot_mentioned=bot_mentioned(update, context),
        )
    elif type(context) == ContextTypes.CALLBACK_TYPE:
        return Context(
            chat_id=update.callback_query.message.chat_id,
            thread_id=None,
            is_bot_mentioned=False,
        )


def get_person(update: Update, context) -> Person:
    if type(context) == ContextTypes.DEFAULT_TYPE:
        return Person(
            user_id=update.message.from_user.id,
            user_handle=update.message.from_user.username,
        )
    elif type(context) == ContextTypes.CALLBACK_TYPE:
        return Person(
            user_id=update.callback_query.from_user.id,
            user_handle=update.callback_query.from_user.username,
        )


def get_message(update: Update) -> Message:
    return Message(
        message=update.message.text,
        image=update.message.photo,
        voice=update.message.voice,
    )


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


def get_messages_tree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    messages = [update.message.text]
    current_message = update.message
    while current_message.reply_to_message:
        current_message = current_message.reply_to_message
        messages.append(current_message.text)
    return messages


async def get_file_in_memory(
    file_id: str, context: ContextTypes.DEFAULT_TYPE
) -> io.BytesIO:
    file = await context.bot.getFile(file_id)
    file_stream = io.BytesIO()
    await file.download(out=file_stream)
    file_stream.seek(0)
    return file_stream


def get_thread_id(update: Update) -> int | None:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def get_stream_cutoff_values(content: str) -> int:
    """
    Gets the stream cutoff values for the message length
    """
    if len(content) > 1000:
        return 180
    elif len(content) > 200:
        return 120
    elif len(content) > 50:
        return 90
    else:
        return 50


async def wrap_with_indicator(
    update: Update,
    context: CallbackContext,
    coroutine,
    chat_action: constants.ChatAction = "",
    is_inline=False,
):
    """
    Wraps a coroutine while repeatedly sending a chat action to the user.
    """
    task = context.application.create_task(coroutine(), update=update)
    while not task.done():
        if not is_inline:
            context.application.create_task(
                update.effective_chat.send_action(
                    chat_action, message_thread_id=get_thread_id(update)
                )
            )
        try:
            await asyncio.wait_for(asyncio.shield(task), 4.5)
        except asyncio.TimeoutError:
            pass


# TODO: adapt tenacity here
async def edit_message_with_retry(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int | None,
    message_id: str,
    text: str,
    markdown: bool = True,
    is_inline: bool = False,
):
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=int(message_id) if not is_inline else None,
            inline_message_id=message_id if is_inline else None,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN if markdown else None,
        )
    except telegram.error.BadRequest as e:
        if str(e).startswith("Message is not modified"):
            return
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=int(message_id) if not is_inline else None,
                inline_message_id=message_id if is_inline else None,
                text=text,
            )
        except Exception as e:
            logging.warning(f"Failed to edit message: {str(e)}")
            raise e

    except Exception as e:
        logging.warning(str(e))
        raise e
